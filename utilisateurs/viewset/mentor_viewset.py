# utilisateurs/viewset/mentor_viewset.py
"""API du parcours Utilisateur & Mentor (spec SCHOOL_ON_User_Mentor_Journey).

Trois espaces distincts :
- ``MentorJourneyViewSet`` : le candidat construit et soumet sa candidature ;
- ``MentorDirectoryViewSet`` : annuaire public des mentors vérifiés + signalement ;
- ``MentorAdminViewSet`` : file de review admin, décisions traçables et signalements.
"""
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from ..models import (
    LearnerProfile,
    MentorApplication,
    MentorReport,
    MentorSkill,
    Qualification,
    TutorProfile,
    VerificationRecord,
)
from ..serializers.mentor_serializers import (
    LearnerProfileSerializer,
    MentorApplicationAdminSerializer,
    MentorApplicationSerializer,
    MentorApplicationWriteSerializer,
    MentorDirectorySerializer,
    MentorPublicSerializer,
    MentorReportReviewSerializer,
    MentorReportSerializer,
    MentorReviewDecisionSerializer,
    MentorSkillSerializer,
    QualificationSerializer,
    VerificationRecordSerializer,
)
from ..utils.geo_utils import haversine_distance

User = get_user_model()


class MentorJourneyViewSet(viewsets.GenericViewSet):
    """Parcours « devenir mentor » côté candidat.

    - ``GET  /api/mentors/status/``        : statut + checklist + historique ;
    - ``GET  /api/mentors/application/``   : ma candidature courante ;
    - ``POST /api/mentors/application/``   : créée/mise à jour le brouillon ;
    - ``POST /api/mentors/application/submit/`` : soumet pour vérification ;
    - ``GET/POST /api/mentors/skills/``    : compétences déclarées ;
    - ``DELETE   /api/mentors/skills/{id}/`` ;
    - ``GET/POST /api/mentors/qualifications/`` : diplômes et documents ;
    - ``DELETE   /api/mentors/qualifications/{id}/``.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MentorApplicationSerializer

    # ---------------------------------------------------------------- helpers
    def _current_application(self, user, create=False):
        """Retourne la candidature courante (la plus récente non close)."""
        application = (
            MentorApplication.objects.filter(user=user)
            .exclude(status__in=['REJECTED', 'SUSPENDED'])
            .order_by('-created_at')
            .first()
        )
        if application is None and create:
            application = MentorApplication.objects.create(user=user, status='DRAFT')
        return application

    def _tutor_profile(self, user):
        profile, _ = TutorProfile.objects.get_or_create(user=user)
        return profile

    # ----------------------------------------------------------------- status
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Statut courant du parcours mentor + checklist + historique (spec §26, §30)."""
        application = self._current_application(request.user)
        tutor_profile = self._tutor_profile(request.user)
        payload = {
            'mentor_status': tutor_profile.mentor_status,
            'is_verified': tutor_profile.is_verified,
            'verified_at': tutor_profile.verified_at,
            'is_teacher': request.user.is_teacher,
            'application': MentorApplicationSerializer(application, context={'request': request}).data if application else None,
            'badges': (
                (['ACCOUNT_CREATED', 'MENTOR_VERIFIED'] if tutor_profile.is_verified else ['ACCOUNT_CREATED'])
            ),
        }
        return Response(payload)

    # ------------------------------------------------------------- candidature
    @action(detail=False, methods=['get', 'post', 'patch'], url_path='application')
    def application(self, request):
        """Consulte ou complète mon brouillon de candidature (spec §16 à §19)."""
        if request.method == 'GET':
            current = self._current_application(request.user)
            if current is None:
                return Response({'detail': 'Aucune candidature en cours.', 'application': None})
            return Response(MentorApplicationSerializer(current, context={'request': request}).data)

        current = self._current_application(request.user, create=True)
        if not current.is_open and not request.user.is_staff:
            raise PermissionDenied(
                'Cette candidature n’est plus modifiable (statut : %s).' % current.get_status_display()
            )

        serializer = MentorApplicationWriteSerializer(
            current, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        return Response(
            MentorApplicationSerializer(application, context={'request': request}).data
        )

    @action(detail=False, methods=['post'], url_path='application/submit')
    def submit_application(self, request):
        """Soumet la candidature à la vérification (statut PENDING_VERIFICATION)."""
        application = self._current_application(request.user, create=True)
        if application.status in {'VERIFIED', 'SUSPENDED'}:
            raise ValidationError({'detail': 'Cette candidature a déjà été traitée.'})

        checklist = MentorApplicationSerializer(application).data['checklist']
        if not checklist['ready_to_submit']:
            missing = [item['label'] for item in checklist['items'] if not item['done']]
            return Response(
                {
                    'detail': 'La candidature est incomplète.',
                    'missing': missing,
                    'checklist': checklist,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.status = 'PENDING_VERIFICATION'
        application.submitted_at = timezone.now()
        application.save(update_fields=['status', 'submitted_at', 'updated_at'])

        tutor_profile = self._tutor_profile(request.user)
        tutor_profile.mentor_status = 'PENDING_VERIFICATION'
        tutor_profile.save(update_fields=['mentor_status'])

        VerificationRecord.objects.create(
            application=application,
            mentor=request.user,
            verification_type='STATUS',
            status='PENDING',
            reason='Candidature soumise par le candidat.',
        )
        return Response(MentorApplicationSerializer(application, context={'request': request}).data)


    # ------------------------------------------------------------ compétences
    @action(detail=False, methods=['get', 'post'], url_path='skills')
    def skills(self, request):
        """Compétences déclarées du candidat / mentor (spec §19 et §40)."""
        if request.method == 'GET':
            queryset = MentorSkill.objects.filter(user=request.user)
            return Response(MentorSkillSerializer(queryset, many=True).data)

        application = self._current_application(request.user, create=True)
        self._assert_application_open(application)
        serializer = MentorSkillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        skill = serializer.save(user=request.user, application=application)
        return Response(MentorSkillSerializer(skill).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='skills/delete')
    def delete_skill(self, request, pk=None):
        """Supprime une compétence déclarée (uniquement si la candidature est ouverte)."""
        skill = MentorSkill.objects.filter(pk=pk, user=request.user).first()
        if skill is None:
            raise ValidationError({'detail': 'Compétence introuvable.'})
        self._assert_application_open(skill.application)
        skill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # --------------------------------------------------------- qualifications
    @action(detail=False, methods=['get', 'post'], url_path='qualifications')
    def qualifications(self, request):
        """Diplômes et documents du candidat (spec §20 et §41)."""
        if request.method == 'GET':
            queryset = Qualification.objects.filter(user=request.user)
            return Response(QualificationSerializer(queryset, many=True, context={'request': request}).data)

        application = self._current_application(request.user, create=True)
        self._assert_application_open(application)
        serializer = QualificationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        qualification = serializer.save(user=request.user, application=application)
        return Response(
            QualificationSerializer(qualification, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['delete'], url_path='qualifications/delete')
    def delete_qualification(self, request, pk=None):
        """Supprime une qualification déclarée (uniquement si la candidature est ouverte)."""
        qualification = Qualification.objects.filter(pk=pk, user=request.user).first()
        if qualification is None:
            raise ValidationError({'detail': 'Qualification introuvable.'})
        self._assert_application_open(qualification.application)
        qualification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ------------------------------------------------------------------ profil
    @action(detail=False, methods=['get', 'patch'], url_path='profile')
    def profile(self, request):
        """Informations professionnelles publiques du mentor (spec §47)."""
        tutor_profile = self._tutor_profile(request.user)
        if request.method == 'GET':
            return Response(MentorPublicSerializer(tutor_profile, context={'request': request}).data)

        editable = {
            'bio', 'headline', 'city', 'country', 'public_location',
            'hourly_rate', 'years_of_experience', 'is_available',
        }
        for field, value in request.data.items():
            if field in editable:
                setattr(tutor_profile, field, value)
        tutor_profile.save()
        return Response(MentorPublicSerializer(tutor_profile, context={'request': request}).data)

    # ----------------------------------------------------------------- helpers
    def _assert_application_open(self, application):
        if application is None:
            raise ValidationError({'detail': 'Aucune candidature en cours.'})
        if not application.is_open and not self.request.user.is_staff:
            raise PermissionDenied('Cette candidature n’est plus modifiable.')

