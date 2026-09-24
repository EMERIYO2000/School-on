import random
import requests
from django.db import IntegrityError
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth import authenticate, get_user_model
from django.utils.crypto import get_random_string

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse

from django.utils import timezone
from django.db.models import Count, Q

from ..models import ParentProfile, TeacherApplication, TutorProfile
from ..serializers import (
    ClassicRegisterUserSerializer,
    TeacherApplicationSerializer,
    LoginSerializer,
    GoogleAuthSerializer,
    MeSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from ..serializers.feature_serializers import MentorApplicationReviewSerializer

User = get_user_model()


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer  # Permet à drf-spectacular de faire ses inspections

    def get_tokens_for_user(self, user):
        """Génère manuellement les tokens JWT pour l'utilisateur"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @extend_schema(
        summary="Inscription classique",
        request=ClassicRegisterUserSerializer,
        responses={
            201: OpenApiResponse(description="Compte créé avec succès !"),
            400: OpenApiResponse(description="Détails de l'erreur de validation")
        }
    )
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """Endpoint : /api/auth/register/"""
        serialiser = ClassicRegisterUserSerializer(data=request.data)
        if serialiser.is_valid():
            try:
                user = serialiser.save()
            except IntegrityError:
                return Response(
                    {'detail': "L'email ou le nom d'utilisateur est déjà utilisé."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            tokens = self.get_tokens_for_user(user)
            return Response({
                "message": "Compte créé avec succès !",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.get_full_name(),
                    "username": user.username,
                    "user_type": user.user_type,
                    "is_parent": user.is_parent,
                    "is_teacher": user.is_teacher,
                },
                "access": tokens['access'],
                "refresh": tokens['refresh']
            }, status=status.HTTP_201_CREATED)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Devenir parent",
        responses={200: MeSerializer, 400: OpenApiResponse(description="Changement de rôle impossible")}
    )
    @action(detail=False, methods=['post'], url_path='become-parent', permission_classes=[IsAuthenticated])
    def become_parent(self, request):
        if request.user.is_teacher or request.user.user_type == 'TEACHER':
            return Response(
                {'error': 'Un compte mentor ne peut pas devenir parent directement.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        user.user_type = 'PARENT'
        user.is_parent = True
        user.is_teacher = False
        user.save(update_fields=['user_type', 'is_parent', 'is_teacher'])
        ParentProfile.objects.get_or_create(user=user)
        return Response(MeSerializer(user).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Postuler pour devenir mentor",
        request=TeacherApplicationSerializer,
        responses={201: TeacherApplicationSerializer, 400: OpenApiResponse(description="Candidature impossible")}
    )
    @action(detail=False, methods=['post'], url_path='become-mentor', permission_classes=[IsAuthenticated])
    def become_mentor(self, request):
        if request.user.is_parent or request.user.user_type == 'PARENT':
            return Response(
                {'error': 'Un compte parent ne peut pas devenir mentor directement.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.is_teacher or request.user.user_type == 'TEACHER':
            return Response({'error': 'Vous êtes déjà mentor.'}, status=status.HTTP_400_BAD_REQUEST)
        if TeacherApplication.objects.filter(user=request.user, status='pending').exists():
            return Response({'error': 'Votre candidature est déjà en attente de validation.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TeacherApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save(user=request.user)

        tutor_profile, _ = TutorProfile.objects.get_or_create(user=request.user)
        if application.identity_card:
            tutor_profile.identity_card = application.identity_card
        if application.diploma:
            tutor_profile.diploma = application.diploma
        tutor_profile.save(update_fields=['identity_card', 'diploma'])

        return Response(TeacherApplicationSerializer(application).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Lister les candidatures mentor",
        responses={200: TeacherApplicationSerializer(many=True), 403: OpenApiResponse(description='Accès refusé')}
    )
    @action(detail=False, methods=['get'], url_path='mentor-applications', permission_classes=[IsAuthenticated])
    def list_mentor_applications(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Accès réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)

        queryset = TeacherApplication.objects.select_related('user', 'reviewed_by').order_by('-created_at')
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return Response(TeacherApplicationSerializer(queryset, many=True).data)

    @extend_schema(
        summary="Obtenir le détail d’une candidature mentor",
        responses={200: TeacherApplicationSerializer, 403: OpenApiResponse(description='Accès refusé'), 404: OpenApiResponse(description='Candidature introuvable')}
    )
    @action(detail=False, methods=['get'], url_path=r'mentor-applications/(?P<pk>[^/.]+)', permission_classes=[IsAuthenticated])
    def get_mentor_application(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'Accès réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            application = TeacherApplication.objects.select_related('user', 'reviewed_by').get(pk=pk)
        except TeacherApplication.DoesNotExist:
            return Response({'error': 'Candidature introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(TeacherApplicationSerializer(application).data)

    @extend_schema(
        summary="Statistiques des candidatures mentor",
        responses={200: OpenApiResponse(description='Statistiques de candidature')}
    )
    @action(detail=False, methods=['get'], url_path='mentor-applications/stats', permission_classes=[IsAuthenticated])
    def mentor_application_stats(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Accès réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)

        counts = dict(
            TeacherApplication.objects.values_list('status').annotate(total=Count('id'))
        )
        payload = {
            'total': TeacherApplication.objects.count(),
            'pending': counts.get('pending', 0),
            'approved': counts.get('approved', 0),
            'rejected': counts.get('rejected', 0),
        }
        return Response(payload)

    @extend_schema(
        summary="Valider ou refuser une candidature mentor",
        request=MentorApplicationReviewSerializer,
        responses={200: TeacherApplicationSerializer, 400: OpenApiResponse(description='Demande de validation invalide'), 403: OpenApiResponse(description='Accès refusé')}
    )
    @action(detail=False, methods=['post'], url_path=r'mentor-applications/(?P<pk>[^/.]+)/review', permission_classes=[IsAuthenticated])
    def review_mentor_application(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'Accès réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            application = TeacherApplication.objects.select_related('user').get(pk=pk)
        except TeacherApplication.DoesNotExist:
            return Response({'error': 'Candidature introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        if application.status != 'pending':
            return Response({'error': 'Cette candidature a déjà été traitée.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MentorApplicationReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data['action']
        review_note = serializer.validated_data.get('review_note', '').strip()

        if action == 'approve':
            application.status = 'approved'
            application.review_note = review_note or 'Candidature approuvée par l’administration.'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save(update_fields=['status', 'review_note', 'reviewed_by', 'reviewed_at'])

            user = application.user
            user.is_teacher = True
            user.is_parent = False
            user.user_type = 'TEACHER'
            user.save(update_fields=['is_teacher', 'is_parent', 'user_type'])

            tutor_profile, _ = TutorProfile.objects.get_or_create(user=user)
            tutor_profile.bio = tutor_profile.bio or application.bio
            tutor_profile.skills = tutor_profile.skills or application.skills
            tutor_profile.identity_card = tutor_profile.identity_card or application.identity_card
            tutor_profile.diploma = tutor_profile.diploma or application.diploma
            tutor_profile.is_verified = True
            tutor_profile.save(update_fields=['bio', 'skills', 'identity_card', 'diploma', 'is_verified'])

            return Response({
                'message': 'Candidature mentor approuvée.',
                'application': TeacherApplicationSerializer(application).data,
            })

        application.status = 'rejected'
        application.review_note = review_note or 'Candidature rejetée par l’administration.'
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.save(update_fields=['status', 'review_note', 'reviewed_by', 'reviewed_at'])
        return Response({
            'message': 'Candidature mentor rejetée.',
            'application': TeacherApplicationSerializer(application).data,
        })

    @extend_schema(
        summary="Connexion utilisateur",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="Connexion réussie !"),
            400: OpenApiResponse(description="Données invalides"),
            401: OpenApiResponse(description="Identifiants invalides")
        }
    )
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """Endpoint : /api/auth/login/"""
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        login_id = serializer.validated_data['login_id']
        password = serializer.validated_data['password']

        user = User.objects.filter(email__iexact=login_id).first()
        if user is None:
            user = User.objects.filter(username__iexact=login_id).first()

        if user is not None and user.check_password(password):
            if not user.is_active:
                return Response({"error": "Ce compte est désactivé."}, status=status.HTTP_403_FORBIDDEN)

            tokens = self.get_tokens_for_user(user)

            return Response({
                "message": "Connexion réussie !",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.get_full_name(),
                    "username": user.username,
                    "is_teacher": user.is_teacher
                },
                "access": tokens['access'],
                "refresh": tokens['refresh']
            }, status=status.HTTP_200_OK)

        return Response(
            {"error": "Identifiants invalides. Veuillez réessayer."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    @extend_schema(
        summary="Récupérer l'utilisateur connecté",
        responses={200: MeSerializer}
    )
    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        """Endpoint : /api/auth/me/"""
        serialiser = MeSerializer(request.user)
        return Response(serialiser.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Changer le mot de passe",
        request=ChangePasswordSerializer,
        responses={200: OpenApiResponse(description="Mot de passe modifié avec succès.")}
    )
    @action(detail=False, methods=['post'], url_path='change-password', permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Endpoint : /api/auth/change-password/"""
        serializer = ChangePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.check_password(serializer.validated_data['older_password']):
            return Response({"error": "L'ancien mot de passe est incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({"message": "Mot de passe modifié avec succès."}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Demande d'OTP de réinitialisation",
        request=PasswordResetRequestSerializer,
        responses={200: OpenApiResponse(description="E-mail d'instruction envoyé")}
    )
    @action(detail=False, methods=['post'], url_path='password-reset-request')
    def password_reset_request(self, request):
        """Endpoint : /api/auth/password-reset-request/"""
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            otp_code = str(random.randint(100000, 999999))
            cache.set(f"reset_code_{email}", otp_code, timeout=900)  # Valide 15 mins

            send_mail(
                subject="Réinitialisation de votre mot de passe - SCHOOL ON",
                message=f"Bonjour {user.first_name},\nVotre code de réinitialisation est : {otp_code}\nIl expire dans 15 minutes.",
                from_email="noreply@schoolon.com",
                recipient_list=[email],
                fail_silently=True
            )
        except User.DoesNotExist:
            pass

        return Response(
            {"message": "Si cet e-mail correspond à un compte, un code y a été envoyé."},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Validation de l'OTP et nouveau mot de passe",
        request=PasswordResetConfirmSerializer,
        responses={200: OpenApiResponse(description="Mot de passe réinitialisé avec succès !")}
    )
    @action(detail=False, methods=['post'], url_path='password-reset-confirm')
    def password_reset_confirm(self, request):
        """Endpoint : POST /api/auth/password-reset-confirm/"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']

        cached_code = cache.get(f"reset_code_{email}")
        if not cached_code or cached_code != code:
            return Response({"error": "Le code est invalide ou a expiré."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            cache.delete(f"reset_code_{email}")
            return Response({"message": "Mot de passe réinitialisé avec succès !"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)















# # from google.oauth2 import id_token
# # from google.auth.transport import requests as google_requests
# import random
# import requests
# from drf_spectacular.utils import extend_schema
# from django.utils.crypto import get_random_string
# from rest_framework import status, viewsets
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from django.core.cache import cache
# from django.core.mail import send_mail
# from django.contrib.auth import authenticate, get_user_model
# from rest_framework_simplejwt.tokens import RefreshToken
# from ..serializers import (
#         ClassicRegisterUserSerializer,
#         LoginSerializer,
#         GoogleAuthSerializer,
#         MeSerializer,
#         ChangePasswordSerializer,
#         PasswordResetRequestSerializer,
#         PasswordResetConfirmSerializer
#     )

# User = get_user_model()


# class AuthViewSet(viewsets.ViewSet):
#     permission_classes = [AllowAny]
#     serializer_class = LoginSerializer
#     def get_tokens_for_user(self, user):
#         """Génère manuellement les tokens JWT pour l'utilisateur"""
#         refresh = RefreshToken.for_user(user)
#         return {
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#         }
    
    
    
#     @extend_schema(
#         request=ClassicRegisterUserSerializer,
#         responses={
#             201: {"message": "Compte créé avec succès !",
#                    "user": {"id": "int", "email": "string", "full_name  ": "string", "username": "string"},
#                    "tokens": {"refresh": "string", "access": "string"}},
#             400: {"error": "Détails de l'erreur de validation"}
#         })
#     @action(detail=False, methods=['post'], url_path='register')
#     def register(self, request):
#         """Endpoint : /api/auth/register/"""
#         serialiser = ClassicRegisterUserSerializer(data=request.data)
#         if serialiser.is_valid():
#             user = serialiser.save()
#             tokens = self.get_tokens_for_user(user)
#             return Response({
#                 "message": "Compte créé avec succès !",
#                 "user": {"id": user.id, "email": user.email, "full_name": user.get_full_name(), "username": user.username},
#                 "tokens": tokens
#             }, status=status.HTTP_201_CREATED)
#         return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
#     # @extend_schema(
#     #     request=GoogleAuthSerializer,
#     #     responses={
#     #         200: {"message": "Connexion réussie via Google !",
#     #                "user": {"id": "int", "email": "string", "full_name": "string", "username": "string", "is_teacher": "boolean"},
#     #                "tokens": {"refresh": "string", "access": "string"}},
#     #         400: {"error": "Détails de l'erreur"}
#     #     }
#     # )
#     # @action(detail=False, methods=['post'], url_path='google')
#     # def register_or_login_google(self, request):
#     #     """Endpoint : /api/auth/google/"""
#     #     serializer = GoogleAuthSerializer(data=request.data)
#     #     if not serializer.is_valid():
#     #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#     #     token = serializer.validated_data['id_token']
        
#     #     if not token:
#     #         return Response({"error": "Le champ id_token est requis"}, status=status.HTTP_400_BAD_REQUEST)
        
#     #     try:
#     #         # 1. Validation du token auprès de Google
#     #         # Remplacer 'VOTRE_GOOGLE_CLIENT_ID' par ton identifiant client Google
#     #         idinfo = id_token.verify_oauth2_token(token, requests.Request(), 'VOTRE_GOOGLE_CLIENT_ID')
            
#     #         email = idinfo.get('email')
#     #         first_name = idinfo.get('given_name', '')
#     #         last_name = idinfo.get('family_name', '')
            
#     #     except ValueError:
#     #         return Response({"error": "Token Google invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)
        
#     #     # 2. Logique de création ou de connexion
#     #     user, created = User.objects.get_or_create(
#     #         email=email,
#     #         defaults={
#     #             'username': email,
#     #             'first_name': first_name,
#     #             'last_name': last_name,
#     #             # On génère un mot de passe aléatoire inutilisable puisque l'accès se fait via Google
#     #             'password': get_random_string(40) 
#     #         }
#     #     )
        
#     #     # 3. Réponse avec les accès
#     #     tokens = self.get_tokens_for_user(user)
#     #     message = "Inscription réussie via Google !" if created else "Connexion réussie via Google !"
        
#     #     return Response({
#     #         "message": message,
#     #         "user": {
#     #             "id": user.id,
#     #             "email": user.email,
#     #             "full_name": user.get_full_name(),
#     #             "username": user.username,
#     #             "is_teacher": user.is_teacher
#     #         },
#     #         "tokens": tokens
#     #     }, status=status.HTTP_200_OK)
    
    
    
    
#     @extend_schema(
#         request=LoginSerializer,
#         responses={
#             200: {"message": "Connexion réussie !",
#                    "user": {"id": "int", "email": "string", "first_name": "string", "last_name": "string", "username": "string", "is_teacher": "boolean"},
#                    "tokens": {"refresh": "string", "access": "string"}},
#             400: {"error": "Détails de l'erreur"}
#         }
#     )
#     @action(detail=False, methods=['post'], url_path='login')
#     def login(self, request):
#         """Endpoint : /api/auth/login/"""
#         serializer = LoginSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         login_id = serializer.validated_data['login_id']
#         password = serializer.validated_data['password']
        
#         # C'est ici que la magie de notre backend personnalisé opère !
#         # Django va chercher 'login_id' dans le champ email ET dans le champ username.
#         user = authenticate(request, username=login_id, password=password)
        
#         if user is not None:
#             if not user.is_active:
#                 return Response({"error": "Ce compte est désactivé."}, status=status.HTTP_403_FORBIDDEN)
                
#             # Génération des tokens JWT pour la session de l'utilisateur
#             tokens = self.get_tokens_for_user(user)
            
#             return Response({
#                 "message": "Connexion réussie !",
#                 "user": {
#                     "id": user.id,
#                     "email": user.email,
#                     "full_name": user.get_full_name(),
#                     "username": user.username,
#                     "is_teacher": user.is_teacher  # Permet au frontend de savoir s'il faut afficher l'espace mentor
#                 },
#                 "tokens": tokens
#             }, status=status.HTTP_200_OK)
            
#         # Sécurité : On reste vague sur l'erreur pour éviter de donner des indices aux hackers
#         return Response(
#             {"error": "Identifiants invalides. Veuillez réessayer."}, 
#             status=status.HTTP_401_UNAUTHORIZED
#         )


#     @action(detail=False, methods=['get'], url_path='me', permission_classes=IsAuthenticated)
#     def me(self, request):
#         serialiser = MeSerializer(request.user)
#         return Response(serialiser.data, status=status.HTTP_200_OK)

#     @action(detail=False, methods=['post'], url_path='change-password', permission_classes=IsAuthenticated)
#     def change_password(self, request):
#         serializer = ChangePasswordSerializer(data=request.data)
        
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         if not request.user.check_password(serializer.validated_data['older_password']):
#             return Response({"error": "L'ancien mot de passe est incorrect."}, status=status.HTTP_400_BAD_REQUEST)

#         request.user.set_password(serializer.validated_data['new_password'])
#         request.user.save()
#         return Response({"message": "Mot de passe modifié avec succès."}, status=status.HTTP_200_OK)

#     @action(detail=False, methods=['post'], url_path='password-reset-request')
#     def password_reset_request(self, request):
#         serializer = PasswordResetRequestSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         email = serializer.validated_data['email']
#         try:
#             user = User.objects.get(email=email)
#             otp_code = str(random.randint(100000, 999999))
#             cache.set(f"reset_code_{email}", otp_code, timeout=900)  # Valide 15 mins

#             send_mail(
#                 subject="Réinitialisation de votre mot de passe - SCHOOL ON",
#                 message=f"Bonjour {user.first_name},\nVotre code de réinitialisation est : {otp_code}\nIl expire dans 15 minutes.",
#                 from_email="noreply@schoolon.com",
#                 recipient_list=[email],
#                 fail_silently=True
#             )
#         except User.DoesNotExist:
#             pass

#         return Response(
#             {"message": "Si cet e-mail correspond à un compte, un code y a été envoyé."},
#             status=status.HTTP_200_OK
#         )

#     @action(detail=False, methods=['post'], url_path='password-reset-confirm')
#     def password_reset_confirm(self, request):
#         """Endpoint : POST /api/auth/password-reset-confirm/"""
#         serializer = PasswordResetConfirmSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         email = serializer.validated_data['email']
#         code = serializer.validated_data['code']
#         new_password = serializer.validated_data['new_password']

#         cached_code = cache.get(f"reset_code_{email}")
#         if not cached_code or cached_code != code:
#             return Response({"error": "Le code est invalide ou a expiré."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.get(email=email)
#             user.set_password(new_password)
#             user.save()
#             cache.delete(f"reset_code_{email}")
#             return Response({"message": "Mot de passe réinitialisé avec succès !"}, status=status.HTTP_200_OK)
#         except User.DoesNotExist:
#             return Response({"error": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)