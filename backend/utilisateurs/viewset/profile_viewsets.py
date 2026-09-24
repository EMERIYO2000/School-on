from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import LearnerProfile, MentorApplication, ParentChildRelation, ParentProfile, TutorProfile
from ..serializers.feature_serializers import LocationUpdateSerializer, ParentChildRequestSerializer
from ..serializers.mentor_serializers import LearnerProfileSerializer, MentorApplicationSerializer
from ..serializers.profile_serializers import AvatarSerializer, ParentProfileSerializer, TutorProfileSerializer, UpdateTutorProfileSerializer, UserDetailSerializer

User = get_user_model()


class ProfileViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    @extend_schema(
        summary='Recuperer le profil complet de l utilisateur connecte',
        responses={200: inline_serializer(
            name='CurrentProfileResponse',
            fields={
                'user': UserDetailSerializer(),
                'tutor_profile': TutorProfileSerializer(required=False),
                'parent_profile': ParentProfileSerializer(required=False),
            },
        )},
    )
    @action(detail=False, methods=['get'], url_path='me')
    def get_my_profile(self, request):
        user = request.user
        data = {'user': UserDetailSerializer(user).data}
        if user.is_teacher and hasattr(user, 'tutor_profile'):
            data['tutor_profile'] = TutorProfileSerializer(user.tutor_profile).data
        elif hasattr(user, 'tutor_profile'):
            # Un compte n'est pas encore mentor, mais le profil existe déjà
            # (brouillon de candidature) : on l'expose pour l'écran de vérification.
            data['tutor_profile'] = TutorProfileSerializer(user.tutor_profile).data
        if user.is_parent and hasattr(user, 'parent_profile'):
            data['parent_profile'] = ParentProfileSerializer(user.parent_profile).data

        learner_profile, _ = LearnerProfile.objects.get_or_create(user=user)
        data['learner_profile'] = LearnerProfileSerializer(learner_profile).data

        application = (
            MentorApplication.objects.filter(user=user)
            .order_by('-created_at')
            .first()
        )
        if application:
            data['mentor_application'] = MentorApplicationSerializer(
                application, context={'request': request}
            ).data
        return Response(data)

    @extend_schema(summary='Mettre a jour la photo de profil', request=AvatarSerializer, responses={200: OpenApiResponse(description='Avatar mis a jour.')})
    @action(detail=False, methods=['post'], url_path='avatar')
    def upload_avatar(self, request):
        serializer = AvatarSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Avatar mis a jour.', 'avatar': request.user.avatar.url if request.user.avatar else None})

    @extend_schema(summary='Consulter ou completer le profil apprenant', request=LearnerProfileSerializer, responses={200: LearnerProfileSerializer})
    @action(detail=False, methods=['get', 'patch', 'put'], url_path='learner')
    def learner_profile(self, request):
        """Profil apprenant et progression du profil (spec §12 et §13)."""
        profile, _ = LearnerProfile.objects.get_or_create(user=request.user)
        if request.method == 'GET':
            return Response(LearnerProfileSerializer(profile).data)
        serializer = LearnerProfileSerializer(profile, data=request.data, partial=request.method == 'PATCH')
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(LearnerProfileSerializer(profile).data)

    @extend_schema(summary='Mettre a jour le profil tuteur', request=UpdateTutorProfileSerializer, responses={200: TutorProfileSerializer})
    @action(detail=False, methods=['patch', 'put'], url_path='tutor')
    def update_tutor_profile(self, request):
        # Un utilisateur n'a pas encore besoin d'être "enseignant" pour préparer
        # son profil : le statut mentor s'obtient après vérification (spec §15).
        tutor_profile, _ = TutorProfile.objects.get_or_create(user=request.user)
        serializer = UpdateTutorProfileSerializer(tutor_profile, data=request.data, partial=request.method == 'PATCH')
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TutorProfileSerializer(tutor_profile).data)

    @extend_schema(summary='Demander le rattachement d un enfant', request=ParentChildRequestSerializer, responses={201: OpenApiResponse(description='Demande creee.')}, deprecated=True)
    @action(detail=False, methods=['post'], url_path='link-child')
    def link_child(self, request):
        if not request.user.is_parent:
            return Response({'error': 'Reserve aux comptes parents.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ParentChildRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data['child_identifier'].strip()
        child = User.objects.filter(email__iexact=identifier).first() or User.objects.filter(username=identifier).first()
        if child is None:
            return Response({'error': 'Utilisateur introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        if child == request.user:
            return Response({'error': 'Vous ne pouvez pas vous ajouter vous-meme.'}, status=status.HTTP_400_BAD_REQUEST)
        relation, _ = ParentChildRelation.objects.get_or_create(parent=request.user, child=child, defaults={'status': 'PENDING'})
        if relation.status == 'ACCEPTED':
            return Response({'error': 'Cet enfant est deja rattache.'}, status=status.HTTP_400_BAD_REQUEST)
        if relation.status == 'REJECTED':
            relation.status = 'PENDING'
            relation.save(update_fields=['status'])
        return Response({'message': 'Demande de rattachement envoyee.', 'relation_id': relation.id}, status=status.HTTP_201_CREATED)

    @extend_schema(summary='Mettre a jour les coordonnees GPS', request=LocationUpdateSerializer, responses={200: OpenApiResponse(description='Position mise a jour.')})
    @action(detail=False, methods=['patch'], url_path='location')
    def update_location(self, request):
        serializer = LocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.latitude = serializer.validated_data['latitude']
        request.user.longitude = serializer.validated_data['longitude']
        request.user.save(update_fields=['latitude', 'longitude'])
        return Response({'message': 'Position GPS mise a jour.'})
