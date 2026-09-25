from rest_framework import serializers
from django.conf import settings

from .models import Certificate, CertificationProgress, FinalProject


class CertificateSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.title', read_only=True)
    recipient_name = serializers.SerializerMethodField()
    verification_url = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ('certificate_id', 'course_name', 'recipient_name', 'mentor_name', 'final_score', 'student_signature_text', 'study_started_at', 'study_completed_at', 'status', 'issued_at', 'verification_url', 'pdf_url')
        read_only_fields = fields

    def get_recipient_name(self, obj):
        return obj.student.get_full_name() or obj.student.username

    def get_verification_url(self, obj):
        base_url = getattr(settings, 'CERTIFICATE_PUBLIC_BASE_URL', '').rstrip('/')
        if base_url:
            return f'{base_url}/certificate/{obj.certificate_id}'
        request = self.context.get('request')
        return request.build_absolute_uri(f'/certificate/{obj.certificate_id}') if request else f'/certificate/{obj.certificate_id}'

    def get_pdf_url(self, obj):
        request = self.context.get('request')
        path = f'/api/certificates/{obj.certificate_id}/download/'
        return request.build_absolute_uri(path) if request else path


class FinalProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalProject
        fields = ('id', 'course', 'submission', 'score', 'status', 'reviewed_at', 'created_at')
        read_only_fields = ('id', 'score', 'status', 'reviewed_at', 'created_at')


class CertificationProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificationProgress
        fields = ('course', 'status', 'mentor_approved', 'updated_at')
        read_only_fields = fields


class CertificateSignatureSerializer(serializers.Serializer):
    signature_text = serializers.CharField(max_length=255, required=False, allow_blank=False)
