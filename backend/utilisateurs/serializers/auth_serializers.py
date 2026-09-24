from rest_framework import serializers
from utilisateurs.models import CustomUser
from django.contrib.auth.password_validation import validate_password


class ClassicRegisterUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True, required=True, min_length=2)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'username', 'email', 'password', 'confirm_password', 'phone_number', 'user_type']

    def validate_email(self, value):
        email_clean = value.lower().strip()
        if CustomUser.objects.filter(email=email_clean).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return email_clean

    def validate_username(self, value):
        username_clean = value.strip()
        if username_clean and CustomUser.objects.filter(username__iexact=username_clean).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username_clean

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        full_name = validated_data.pop('full_name')
        username = validated_data.get('username', None)
        email = validated_data.get('email', '')
        user_type = validated_data.get('user_type', 'STUDENT')

        name_parts = full_name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user = CustomUser.objects.create_user(
            username=username if username else email,
            email=email,
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
            phone_number=validated_data.get("phone_number", ''),
            user_type=user_type,
            is_teacher=(user_type == 'TEACHER'),
            is_parent=(user_type == 'PARENT'),
        )
        return user

class LoginSerializer(serializers.Serializer):
    login_id = serializers.CharField(
        required=True, 
        help_text="Peut être l'adresse email ou le nom d'utilisateur."
    )
    password = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )
class GoogleAuthSerializer(serializers.Serializer):
    """Reçoit le token Google envoyé par le frontend"""
    id_token = serializers.CharField(required=True)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

class MeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    mentor_status = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "email",
            "phone_number",
            "avatar",
            "is_teacher",
            "is_parent",
            "is_staff",
            "is_premium_subscriber",
            "first_name",
            "last_name",
            "full_name",
            "user_type",
            "mentor_status",
        )
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_mentor_status(self, obj):
        """Statut du parcours de vérification mentor (spec User & Mentor Journey §26)."""
        if not hasattr(obj, 'tutor_profile'):
            return 'DRAFT'
        return obj.tutor_profile.mentor_status

class ChangePasswordSerializer(serializers.Serializer):
    older_password = serializers.CharField(min_length=8, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Les nouveaux mots de passe ne correspondent pas.")
        return super().validate(attrs)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
