from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import LearnerProfile, TutorProfile, ParentProfile
User = get_user_model()


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("avatar",)


class UpdateIdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number')


class LearnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearnerProfile
        fields = ('date_of_birth', 'country', 'city', 'education_level', 'school_name', 'interests', 'learning_goal', 'profile_completion')
        read_only_fields = ('profile_completion',)

    def update(self, instance, validated_data):
        result = super().update(instance, validated_data)
        required = (result.date_of_birth, result.country, result.city, result.education_level, result.learning_goal)
        result.profile_completion = round(sum(bool(value) for value in required) * 100 / len(required))
        result.save(update_fields=('profile_completion', 'updated_at'))
        return result


class UserDetailSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

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
            "date_joined",
        )
        read_only_fields = fields

    def get_avatar(self, obj):
        if not obj.avatar:
            return None
        url = obj.avatar.url
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url

class TutorProfileSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    class Meta:
        model = TutorProfile
        fields = "__all__"

class UpdateTutorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorProfile
        fields = (
            "bio",
            "skills",
            "certifications",
            "hourly_rate",
            "city",
            "country",
            "is_available"
        )

class ParentProfileSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    children = UserDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model =ParentProfile
        fields = "__all__"
