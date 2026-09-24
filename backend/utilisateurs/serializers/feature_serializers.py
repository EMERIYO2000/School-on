# utilisateurs/serializers/feature_serializers.py
from decimal import Decimal

from decimal import Decimal

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import ParentChildRelation, TeacherApplication, TutorProfile

User = get_user_model()

class LocationUpdateSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=Decimal('-90'),
        max_value=Decimal('90'),
        required=True
    )
    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=Decimal('-180'),
        max_value=Decimal('180'),
        required=True
    )

class FCMTokenSerializer(serializers.Serializer):
    fcm_token = serializers.CharField(max_length=255, required=True)

class ParentChildRequestSerializer(serializers.Serializer):
    child_identifier = serializers.CharField(help_text="Email ou Nom d'utilisateur de l'enfant")

class ParentChildResponseSerializer(serializers.Serializer):
    relation_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['accept', 'reject'])

class TutorDocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorProfile
        fields = ['identity_card', 'diploma']
        
class NearbyTutorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    latitude = serializers.DecimalField(source='user.latitude', max_digits=9, decimal_places=6, read_only=True)
    longitude = serializers.DecimalField(source='user.longitude', max_digits=9, decimal_places=6, read_only=True)
    distance_km = serializers.FloatField(read_only=True)

    class Meta:
        model = TutorProfile
        fields = [
            'id', 
            'full_name', 
            'avatar', 
            'bio', 
            'hourly_rate', 
            'city', 
            'latitude', 
            'longitude', 
            'distance_km',
            'is_verified'
        ]


class TeacherApplicationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    reviewed_by_email = serializers.EmailField(source='reviewed_by.email', read_only=True, allow_null=True)

    class Meta:
        model = TeacherApplication
        fields = (
            'id',
            'user',
            'user_email',
            'bio',
            'skills',
            'certificates',
            'identity_card',
            'diploma',
            'status',
            'review_note',
            'reviewed_by',
            'reviewed_by_email',
            'reviewed_at',
            'created_at',
        )
        read_only_fields = (
            'id',
            'user',
            'user_email',
            'status',
            'review_note',
            'reviewed_by',
            'reviewed_by_email',
            'reviewed_at',
            'created_at',
        )


class MentorApplicationReviewSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    review_note = serializers.CharField(required=False, allow_blank=True, default='')
