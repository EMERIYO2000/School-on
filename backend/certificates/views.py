from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import FileResponse
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Certificate, CertificationProgress, FinalProject
from .serializers import CertificateSerializer, CertificationProgressSerializer, CertificateSignatureSerializer, FinalProjectSerializer
from .services import certification_status, issue_certificate_if_eligible
from .pdf import render_certificate_pdf


class MyCertificatesView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CertificateSerializer

    def get_queryset(self):
        return Certificate.objects.filter(student=self.request.user).select_related('course', 'student')


class CertificateDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CertificateSerializer
    lookup_field = 'certificate_id'

    def get_queryset(self):
        return Certificate.objects.filter(student=self.request.user).select_related('course', 'student', 'mentor')


class CertificateDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, certificate_id):
        certificate = get_object_or_404(
            Certificate.objects.select_related('course', 'student', 'mentor'),
            certificate_id=certificate_id,
            student=request.user,
        )
        if certificate.status != 'VALID':
            return Response({'detail': 'Ce certificat n’est plus valide.'}, status=status.HTTP_410_GONE)
        try:
            pdf = render_certificate_pdf(certificate)
        except FileNotFoundError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response = FileResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{certificate.certificate_id}.pdf"'
        return response


class CertificateSignatureView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, certificate_id):
        certificate = get_object_or_404(Certificate, certificate_id=certificate_id, student=request.user, status='VALID')
        serializer = CertificateSignatureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificate.student_signature_text = serializer.validated_data['signature_text'].strip()
        certificate.save(update_fields=['student_signature_text'])
        return Response(CertificateSerializer(certificate, context={'request': request}).data)


class VerifyCertificateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, certificate_id):
        certificate = get_object_or_404(
            Certificate.objects.select_related('course', 'student'),
            certificate_id=certificate_id,
        )
        data = CertificateSerializer(certificate, context={'request': request}).data
        data['valid'] = certificate.status == 'VALID'
        return Response(data)


class CertificationStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        from courses.models import Course
        course = get_object_or_404(Course, pk=course_id)
        return Response(certification_status(request.user, course))


class FinalProjectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        from courses.models import Course, Enrollment
        course = get_object_or_404(Course, pk=course_id)
        if not Enrollment.objects.filter(student=request.user, course=course, status='active').exists():
            return Response({'detail': 'Une inscription active est requise.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = FinalProjectSerializer(data={'course': course.id, 'submission': request.data.get('submission', '')})
        serializer.is_valid(raise_exception=True)
        project, _ = FinalProject.objects.update_or_create(
            student=request.user,
            course=course,
            defaults={'submission': serializer.validated_data['submission'], 'status': 'SUBMITTED', 'score': None, 'reviewed_by': None, 'reviewed_at': None},
        )
        return Response(FinalProjectSerializer(project).data, status=status.HTTP_201_CREATED)


class MentorCertificationApprovalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id, student_id):
        from courses.models import Course
        course = get_object_or_404(Course, pk=course_id, teacher=request.user)
        progress = get_object_or_404(CertificationProgress, course=course, student_id=student_id)
        progress.mentor_approved = True
        progress.save(update_fields=['mentor_approved', 'updated_at'])
        certificate = issue_certificate_if_eligible(progress.student, course)
        if not certificate:
            return Response({'detail': 'Les autres conditions de certification ne sont pas encore remplies.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CertificateSerializer(certificate, context={'request': request}).data)
