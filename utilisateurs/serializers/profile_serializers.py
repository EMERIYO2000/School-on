from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import TutorProfile, ParentProfile
User = get_user_model()


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("avatar",)


class UserDetailSerializer(serializers.ModelSerializer):
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
            "is_premium_subscriber"
        )

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