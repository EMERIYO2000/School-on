from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import TutorProfile, ParentProfile
User = get_user_model()


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("avatar",)


class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    mentor_status = serializers.SerializerMethodField()

    class Meta:
        model =User
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "avatar",
            "is_teacher",
            "is_parent",
            "is_premium_subscriber",
            "user_type",
            "full_name",
            "mentor_status",
        )

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_mentor_status(self, obj):
        """Statut du parcours de vérification mentor (spec User & Mentor Journey)."""
        if not hasattr(obj, 'tutor_profile'):
            return 'DRAFT'
        return obj.tutor_profile.mentor_status

class TutorProfileSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    class Meta:
        model = TutorProfile
        fields = "__all__"

class UpdateTutorProfileSerializer(serializers.ModelSerializer):
    """Mise à jour du profil mentor depuis l'écran de vérification (spec §16 à §19)."""
    class Meta:
        model = TutorProfile
        fields = (
            "title",
            "bio",
            "headline",
            "skills",
            "specialties",
            "experience",
            "education",
            "certifications",
            "hourly_rate",
            "session_price",
            "city",
            "country",
            "public_location",
            "years_of_experience",
            "id_document",
            "is_available"
        )

    def validate_specialties(self, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        raise serializers.ValidationError('Les spécialités doivent être une liste ou une chaîne séparée par des virgules.')

class ParentProfileSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    children = UserDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model =ParentProfile
        fields = "__all__"