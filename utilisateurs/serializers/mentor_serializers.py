# utilisateurs/serializers/mentor_serializers.py
"""Sérialiseurs du parcours Utilisateur & Mentor (spec SCHOOL_ON_User_Mentor_Journey).

Séparation stricte public / privé (spec §46 et §47) :
- ``MentorPublicSerializer`` n'expose jamais les documents d'identité, l'adresse
  exacte, les notes admin ni les informations internes de vérification ;
- les sérialiseurs « privés » sont réservés au candidat et à l'administration.
"""
from rest_framework import serializers

from ..models import (
    LearnerProfile,
    MentorApplication,
    MentorAssessment,
    MentorInterview,
    MentorReport,
    MentorSkill,
    Qualification,
    TutorProfile,
    VerificationRecord,
)


class LearnerProfileSerializer(serializers.ModelSerializer):
    """Profil apprenant + complétion (spec §12 et §13)."""
    completion = serializers.IntegerField(source='profile_completion', read_only=True)
    completion_hints = serializers.SerializerMethodField()

    class Meta:
        model = LearnerProfile
        fields = [
            'id', 'date_of_birth', 'country', 'city', 'education_level',
            'school_name', 'interests', 'learning_goal', 'completion',
            'completion_hints', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'completion', 'completion_hints', 'created_at', 'updated_at']

    def get_completion_hints(self, obj):
        """Suggestions affichées dans la barre de progression du profil (spec §13)."""
        hints = []
        if not obj.user.avatar:
            hints.append('Ajoutez une photo de profil')
        if not obj.user.phone_number:
            hints.append('Ajoutez votre numéro de téléphone')
        if not obj.city:
            hints.append('Indiquez votre ville')
        if not obj.education_level:
            hints.append('Ajoutez votre niveau scolaire')
        if not obj.interests:
            hints.append('Choisissez vos domaines d’intérêt')
        if not obj.learning_goal:
            hints.append('Décrivez votre objectif d’apprentissage')
        return hints


class MentorSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorSkill
        fields = [
            'id', 'domain', 'specialization', 'declared_level',
            'years_of_experience', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class QualificationSerializer(serializers.ModelSerializer):
    """Qualification vue par son propriétaire ou par l'admin."""
    document_url = serializers.SerializerMethodField()

    class Meta:
        model = Qualification
        fields = [
            'id', 'qualification_type', 'title', 'institution', 'year',
            'document', 'document_url', 'reference', 'verification_status', 'created_at',
        ]
        read_only_fields = ['id', 'document_url', 'verification_status', 'created_at']

    def get_document_url(self, obj):
        if not obj.document:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.document.url) if request else obj.document.url


class VerificationRecordSerializer(serializers.ModelSerializer):
    """Trace des décisions de vérification (spec §31)."""
    verification_type_label = serializers.CharField(source='get_verification_type_display', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = VerificationRecord
        fields = [
            'id', 'verification_type', 'verification_type_label', 'status', 'status_label',
            'reason', 'notes', 'document_reference', 'reviewed_by', 'reviewed_by_name',
            'reviewed_at', 'created_at',
        ]
        read_only_fields = fields

    def get_reviewed_by_name(self, obj):
        if not obj.reviewed_by:
            return None
        return obj.reviewed_by.get_full_name() or obj.reviewed_by.username


class MentorAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorAssessment
        fields = ['id', 'skill', 'score', 'status', 'completed_at', 'created_at']
        read_only_fields = fields


class MentorInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorInterview
        fields = ['id', 'scheduled_at', 'completed_at', 'status', 'notes', 'created_at']
        read_only_fields = fields


class MentorApplicationSerializer(serializers.ModelSerializer):
    """Candidature mentor vue par le candidat lui-même.

    Inclut la checklist utilisée par l'écran de vérification (spec §30) et
    l'historique des décisions de vérification.
    """
    skills = MentorSkillSerializer(many=True, read_only=True)
    qualifications = QualificationSerializer(many=True, read_only=True)
    verification_records = VerificationRecordSerializer(many=True, read_only=True)
    assessments = MentorAssessmentSerializer(many=True, read_only=True)
    interviews = MentorInterviewSerializer(many=True, read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    checklist = serializers.SerializerMethodField()
    public_location = serializers.SerializerMethodField()

    class Meta:
        model = MentorApplication
        fields = [
            'id', 'status', 'status_label', 'legal_name', 'date_of_birth', 'country',
            'city', 'address', 'phone_number', 'motivation', 'professional_bio',
            'public_location', 'checklist', 'submitted_at', 'reviewed_at', 'review_note',
            'skills', 'qualifications', 'verification_records', 'assessments',
            'interviews', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'status_label', 'reviewed_at', 'review_note',
            'submitted_at', 'created_at', 'updated_at',
        ]

    def get_public_location(self, obj):
        """Localisation publique jamais plus précise que « Ville, Pays » (spec §17)."""
        return ', '.join(part for part in [obj.city, obj.country] if part) or None

    def get_checklist(self, obj):
        """Pré-requis de candidature (spec §21 et §30)."""
        items = [
            {
                'key': 'identity',
                'label': 'Informations personnelles',
                'done': bool(obj.legal_name and obj.phone_number and obj.city),
            },
            {'key': 'skills', 'label': 'Compétences déclarées', 'done': obj.skills.exists()},
            {
                'key': 'qualifications',
                'label': 'Diplômes / documents',
                'done': obj.qualifications.exists(),
            },
            {
                'key': 'bio',
                'label': 'Présentation professionnelle',
                'done': len((obj.professional_bio or '').strip()) >= 40,
            },
            {
                'key': 'motivation',
                'label': 'Motivation',
                'done': len((obj.motivation or '').strip()) >= 20,
            },
        ]
        completed = sum(1 for item in items if item['done'])
        return {
            'items': items,
            'completed': completed,
            'total': len(items),
            'ready_to_submit': completed == len(items),
        }


class MentorApplicationAdminSerializer(MentorApplicationSerializer):
    """Candidature vue par l'administration (informations privées autorisées)."""

    class Meta(MentorApplicationSerializer.Meta):
        read_only_fields = ['id', 'created_at', 'updated_at']



class MentorApplicationWriteSerializer(serializers.ModelSerializer):
    """Création / mise à jour d'un brouillon de candidature (spec §16 à §19)."""
    skills = MentorSkillSerializer(many=True, required=False)
    qualifications = QualificationSerializer(many=True, required=False)

    class Meta:
        model = MentorApplication
        fields = [
            'id', 'legal_name', 'date_of_birth', 'country', 'city', 'address',
            'phone_number', 'motivation', 'professional_bio', 'skills', 'qualifications',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        skills_data = validated_data.pop('skills', [])
        qualifications_data = validated_data.pop('qualifications', [])
        user = self.context['request'].user
        application = MentorApplication.objects.create(user=user, **validated_data)
        MentorSkill.objects.bulk_create([
            MentorSkill(user=user, application=application, **skill) for skill in skills_data
        ])
        for qualification in qualifications_data:
            Qualification.objects.create(user=user, application=application, **qualification)
        return application

    def update(self, instance, validated_data):
        skills_data = validated_data.pop('skills', None)
        qualifications_data = validated_data.pop('qualifications', None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if skills_data is not None:
            instance.skills.all().delete()
            MentorSkill.objects.bulk_create([
                MentorSkill(user=instance.user, application=instance, **skill) for skill in skills_data
            ])
        if qualifications_data is not None:
            instance.qualifications.all().delete()
            for qualification in qualifications_data:
                Qualification.objects.create(user=instance.user, application=instance, **qualification)
        return instance


class MentorReviewDecisionSerializer(serializers.Serializer):
    """Décision administrative sur une candidature (spec §30 et §31)."""
    ACTION_CHOICES = [
        ('approve', 'Approuver'),
        ('reject', 'Refuser'),
        ('request_information', 'Demander des informations'),
        ('suspend', 'Suspendre'),
        ('start_review', 'Passer en revue'),
    ]
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True, default='')
    verification_type = serializers.ChoiceField(
        choices=[choice[0] for choice in VerificationRecord.VERIFICATION_TYPES],
        required=False,
        default='STATUS',
    )

    def validate(self, attrs):
        action = attrs['action']
        note = (attrs.get('note') or '').strip()
        if action in {'reject', 'request_information', 'suspend'} and len(note) < 10:
            raise serializers.ValidationError(
                {'note': 'Un motif d’au moins 10 caractères est obligatoire pour cette décision.'}
            )
        attrs['note'] = note
        return attrs


class MentorReportSerializer(serializers.ModelSerializer):
    """Signalement de mentor vu par son auteur et l'administration (spec §32)."""
    reporter_name = serializers.SerializerMethodField()
    mentor_name = serializers.SerializerMethodField()
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    reason_label = serializers.CharField(source='get_reason_display', read_only=True)

    class Meta:
        model = MentorReport
        fields = [
            'id', 'mentor', 'mentor_name', 'reporter', 'reporter_name', 'reason',
            'reason_label', 'details', 'status', 'status_label', 'resolution_note',
            'reviewed_at', 'created_at',
        ]
        read_only_fields = [
            'id', 'reporter', 'reporter_name', 'mentor_name', 'status', 'status_label',
            'resolution_note', 'reviewed_at', 'created_at',
        ]

    def get_reporter_name(self, obj):
        return obj.reporter.get_full_name() or obj.reporter.username

    def get_mentor_name(self, obj):
        return obj.mentor.get_full_name() or obj.mentor.username


class MentorReportReviewSerializer(serializers.Serializer):
    """Traitement d'un signalement par l'administration (spec §33)."""
    STATUS_CHOICES = [
        ('UNDER_REVIEW', 'En cours d’investigation'),
        ('RESOLVED', 'Clôturé'),
        ('DISMISSED', 'Rejeté'),
        ('ACTION_TAKEN', 'Sanction appliquée'),
    ]
    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    resolution_note = serializers.CharField(required=False, allow_blank=True, default='')
    suspend_mentor = serializers.BooleanField(default=False)

    def validate(self, attrs):
        if attrs['status'] in {'ACTION_TAKEN', 'DISMISSED', 'RESOLVED'} and len(attrs.get('resolution_note', '').strip()) < 10:
            raise serializers.ValidationError(
                {'resolution_note': 'Une note de résolution d’au moins 10 caractères est obligatoire.'}
            )
        return attrs



class MentorPublicSerializer(serializers.ModelSerializer):
    """Profil mentor public (spec §27 et §47).

    N'expose JAMAIS : documents d'identité, adresse exacte, notes admin,
    informations internes de vérification.
    """
    user_id = serializers.ReadOnlyField(source='user.id')
    full_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    is_verified = serializers.ReadOnlyField()
    hourly_rate = serializers.FloatField()
    session_price = serializers.FloatField()
    badges = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()

    class Meta:
        model = TutorProfile
        fields = [
            'id', 'user_id', 'full_name', 'avatar', 'title', 'headline', 'bio',
            'city', 'country', 'public_location', 'years_of_experience', 'experience',
            'hourly_rate', 'session_price', 'specialties',
            'is_verified', 'is_available', 'mentor_status', 'verified_at',
            'badges', 'skills', 'stats',
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_avatar(self, obj):
        if not obj.user.avatar:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.user.avatar.url) if request else obj.user.avatar.url

    def get_badges(self, obj):
        """Badges de confiance affichables (spec §27)."""
        badges = ['ACCOUNT_CREATED']
        if obj.mentor_status == 'VERIFIED' and obj.is_verified:
            badges.append('MENTOR_VERIFIED')
        return badges

    def get_skills(self, obj):
        return [
            {
                'domain': skill.domain,
                'specialization': skill.specialization,
                'declared_level': skill.declared_level,
                'years_of_experience': skill.years_of_experience,
            }
            for skill in obj.user.mentor_skills.all()
        ]

    def get_stats(self, obj):
        """Statistiques basées sur des activités réelles (spec §27 et §28)."""
        bookings = obj.tutor_bookings.all()
        completed = bookings.filter(status='COMPLETED').count()
        return {
            'sessions': completed,
            'learners': bookings.values('student').distinct().count(),
            'courses': obj.user.taught_courses.filter(status='PUBLISHED').count(),
        }


class MentorDirectorySerializer(MentorPublicSerializer):
    """Élément de l'annuaire des mentors (liste paginée)."""
    distance_km = serializers.FloatField(read_only=True)

    class Meta(MentorPublicSerializer.Meta):
        fields = MentorPublicSerializer.Meta.fields + ['distance_km']


class PublicLocationSerializer(serializers.Serializer):
    """Mise à jour de la localisation publique d'un mentor (spec §17)."""
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    country = serializers.CharField(max_length=100, required=False, allow_blank=True)

