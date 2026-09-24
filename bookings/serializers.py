from django.utils import timezone
from rest_framework import serializers

from utilisateurs.models import TutorProfile

from .models import Booking, BookingReview


class BookingSerializer(serializers.ModelSerializer):
    mentor = serializers.PrimaryKeyRelatedField(
        source='tutor', queryset=TutorProfile.objects.select_related('user')
    )
    address = serializers.CharField(source='adress', required=False, allow_blank=True)
    scheduled_at = serializers.DateTimeField(write_only=True)
    duration = serializers.IntegerField(write_only=True, min_value=15, max_value=480, default=60)
    subject = serializers.CharField(write_only=True, required=False, allow_blank=True)
    notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    mode = serializers.CharField(write_only=True, required=False, allow_blank=True)
    mentor_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'mentor', 'mentor_name', 'scheduled_at', 'duration', 'subject',
            'notes', 'mode', 'address', 'date_requested', 'time_requested',
            'status', 'student_confirmed', 'mentor_confirmed', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'mentor_name', 'date_requested', 'time_requested', 'status',
            'student_confirmed', 'mentor_confirmed', 'created_at', 'updated_at',
        ]

    def get_mentor_name(self, obj):
        return obj.tutor.user.get_full_name() or obj.tutor.user.username

    def validate(self, attrs):
        scheduled_at = attrs.get('scheduled_at')
        if scheduled_at and scheduled_at <= timezone.now():
            raise serializers.ValidationError({'scheduled_at': 'La session doit être planifiée dans le futur.'})
        tutor = attrs.get('tutor')
        if tutor and not tutor.is_public():
            raise serializers.ValidationError({'mentor': 'Ce mentor n’est pas disponible pour les réservations.'})
        return attrs

    def create(self, validated_data):
        scheduled_at = validated_data.pop('scheduled_at')
        validated_data.pop('duration', None)
        validated_data.pop('subject', None)
        validated_data.pop('notes', None)
        validated_data.pop('mode', None)
        validated_data.setdefault('adress', 'À définir avec le mentor')
        return Booking.objects.create(
            date_requested=scheduled_at.date(),
            time_requested=scheduled_at.time(),
            **validated_data,
        )


class BookingReviewSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = BookingReview
        fields = ['id', 'booking', 'rating', 'comment', 'author_name', 'created_at']
        read_only_fields = ['id', 'booking', 'author_name', 'created_at']

    def get_author_name(self, obj):
        return obj.booking.student.get_full_name() or obj.booking.student.username

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('La note doit être comprise entre 1 et 5.')
        return value
