# utilisateurs/viewset/mentor_admin.py
"""Espace administration du parcours mentor (spec §30, §31 et §33).

Chaque décision importante est journalisée dans un ``VerificationRecord`` :
on peut toujours répondre « qui a validé, quand et pourquoi ».
"""
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from ..models import (
    MentorApplication,
    MentorReport,
    TutorProfile,
    VerificationRecord,
)
from ..serializers.mentor_serializers import (
    MentorApplicationAdminSerializer,
    MentorReportReviewSerializer,
    MentorReportSerializer,
    MentorReviewDecisionSerializer,
    VerificationRecordSerializer,
)

User = get_user_model()

# Charte des décisions administratives -> (statut de candidature, statut de profil,
# statut de l'utilisateur, événement d'historique, is_verified)
ACTION_MAP = {
    'start_review': ('UNDER_REVIEW', None, None, 'IN_PROGRESS'),
    'request_information': ('NEEDS_INFORMATION', None, None, 'INFO_REQUIRED'),
    'approve': ('VERIFIED', 'VERIFIED', None, 'PASSED'),
    'reject': ('REJECTED', 'REJECTED', None, 'FAILED'),
    'suspend': ('SUSPENDED', 'SUSPENDED', None, 'FAILED'),
}


class MentorAdminViewSet(viewsets.GenericViewSet):
    """Review administratif des candidatures et des signalements.

    - ``GET  /api/admin/mentors/applications/``          : file de review (filtre ``status``) ;
    - ``GET  /api/admin/mentors/applications/{id}/``     : dossier complet ;
    - ``POST /api/admin/mentors/applications/{id}/review/`` : décision (approve/reject/request_information/suspend/start_review) ;
    - ``GET  /api/admin/mentors/applications/{id}/history/`` : historique des décisions ;
    - ``GET  /api/admin/mentors/reports/``              : signalements ;
    - ``POST /api/admin/mentors/reports/{id}/resolve/`` : traitement d'un signalement ;
    - ``GET  /api/admin/mentors/stats/``                : compteurs de review.
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = MentorApplicationAdminSerializer

    def get_queryset(self):
        return MentorApplication.objects.select_related(
            'user', 'reviewed_by',
        ).prefetch_related(
            'skills', 'qualifications', 'verification_records',
            'assessments', 'interviews',
        )

    # ------------------------------------------------------------------ liste
    def list(self, request, *args, **kwargs):
        """File de review des candidatures (spec §30)."""
        queryset = self.get_queryset()
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        if request.query_params.get('search'):
            term = request.query_params['search']
            queryset = queryset.filter(
                Q(user__first_name__icontains=term)
                | Q(user__last_name__icontains=term)
                | Q(user__email__icontains=term)
                | Q(legal_name__icontains=term)
            )

        return Response({
            'count': queryset.count(),
            'by_status': [
                {'status': row['status'], 'total': row['total']}
                for row in queryset.values('status').annotate(total=Count('id'))
            ],
            'results': MentorApplicationAdminSerializer(
                queryset, many=True, context={'request': request}
            ).data,
        })

    def retrieve(self, request, pk=None):
        """Dossier complet d'une candidature (espace admin, données privées incluses)."""
        application = self.get_object()
        return Response(
            MentorApplicationAdminSerializer(application, context={'request': request}).data
        )

    # --------------------------------------------------------------- décision
    @action(detail=True, methods=['post'], url_path='review')
    def review(self, request, pk=None):
        """Décision administrative : approve / reject / request_information / suspend.

        Chaque décision est traçée dans un ``VerificationRecord`` (spec §31),
        l'approbation active les droits mentor, et les décisions négatives
        exigent un motif d'au moins 10 caractères.
        """
        application = self.get_object()
        serializer = MentorReviewDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action_name = serializer.validated_data['action']
        note = serializer.validated_data['note']
        verification_type = serializer.validated_data.get('verification_type') or 'STATUS'

        new_status, profile_status, _user_status, event_status = ACTION_MAP[action_name]
        tutor_profile, _ = TutorProfile.objects.get_or_create(user=application.user)

        with transaction.atomic():
            application.status = new_status
            application.reviewed_at = timezone.now()
            application.reviewed_by = request.user
            application.review_note = note
            application.save(
                update_fields=['status', 'reviewed_at', 'reviewed_by', 'review_note', 'updated_at']
            )

            if profile_status:
                tutor_profile.mentor_status = profile_status
                tutor_profile.is_verified = profile_status == 'VERIFIED'
                if profile_status == 'VERIFIED':
                    tutor_profile.verified_at = timezone.now()
                tutor_profile.save(update_fields=['mentor_status', 'is_verified', 'verified_at'])

            if new_status == 'VERIFIED':
                application.user.is_teacher = True
                application.user.user_type = 'TEACHER'
                application.user.save(update_fields=['is_teacher', 'user_type'])
            elif new_status in {'SUSPENDED', 'REJECTED'} and application.user.is_teacher:
                application.user.is_teacher = False
                application.user.save(update_fields=['is_teacher'])

            VerificationRecord.objects.create(
                application=application,
                mentor=application.user,
                verification_type=verification_type,
                status=event_status,
                reviewed_by=request.user,
                reviewed_at=timezone.now(),
                reason=note or f'Décision administrative : {action_name}',
                notes=f'Décision : {action_name}',
            )

        return Response(
            MentorApplicationAdminSerializer(application, context={'request': request}).data
        )

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        """Historique complet des décisions de vérification (spec §31)."""
        application = self.get_object()
        records = VerificationRecord.objects.filter(application=application).select_related('reviewed_by')
        return Response(VerificationRecordSerializer(records, many=True).data)


class MentorReportAdminViewSet(viewsets.GenericViewSet):
    """Traitement des signalements de mentors (spec §32 et §33).

    - ``GET  /api/admin/mentors/reports/``              : liste (filtre ``status``) ;
    - ``POST /api/admin/mentors/reports/{id}/resolve/``  : traitement de l'investigation.
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = MentorReportSerializer

    def get_queryset(self):
        queryset = MentorReport.objects.select_related('mentor', 'reporter', 'reviewed_by')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request, pk=None):
        """Clôture un signalement, avec sanction optionnelle du mentor (spec §33)."""
        report = self.get_object()
        serializer = MentorReportReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        report.status = validated['status']
        report.resolution_note = validated['resolution_note']
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()

        if validated.get('suspend_mentor'):
            report.status = 'ACTION_TAKEN'
            self._suspend_mentor(report, request.user)

        report.save(update_fields=['status', 'resolution_note', 'reviewed_by', 'reviewed_at'])
        return Response(MentorReportSerializer(report).data)

    @staticmethod
    def _suspend_mentor(report, reviewer):
        """Suspend un mentor signalé et écrit la décision dans l'historique."""
        tutor_profile, _ = TutorProfile.objects.get_or_create(user=report.mentor)
        tutor_profile.mentor_status = 'SUSPENDED'
        tutor_profile.is_verified = False
        tutor_profile.save(update_fields=['mentor_status', 'is_verified'])

        if report.mentor.is_teacher:
            report.mentor.is_teacher = False
            report.mentor.save(update_fields=['is_teacher'])

        application = MentorApplication.objects.filter(user=report.mentor).order_by('-created_at').first()
        if application is None:
            return
        application.status = 'SUSPENDED'
        application.review_note = report.resolution_note
        application.reviewed_by = reviewer
        application.reviewed_at = timezone.now()
        application.save(
            update_fields=['status', 'review_note', 'reviewed_by', 'reviewed_at', 'updated_at']
        )
        VerificationRecord.objects.create(
            application=application,
            mentor=report.mentor,
            verification_type='STATUS',
            status='FAILED',
            reviewed_by=reviewer,
            reviewed_at=timezone.now(),
            reason=report.resolution_note,
            notes=f'Sanction suite au signalement #{report.id}',
        )

