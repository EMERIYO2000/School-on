from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import BlacklistedToken, OutstandingToken

from ..models import ParentChildRelation, ParentProfile, TutorProfile
from ..serializers.feature_serializers import FCMTokenSerializer, LocationUpdateSerializer, NearbyTutorSerializer, ParentChildRequestSerializer, ParentChildResponseSerializer, TutorDocumentUploadSerializer
from ..utils.fcm_utils import send_fcm_notification
from ..utils.geo_utils import haversine_distance

User = get_user_model()


class UserFeaturesViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LocationUpdateSerializer

    @extend_schema(request=LocationUpdateSerializer, responses={200: OpenApiResponse(description='Position mise a jour.')})
    @action(detail=False, methods=['patch'], url_path='me/location')
    def update_location(self, request):
        serializer = LocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.latitude = serializer.validated_data['latitude']
        request.user.longitude = serializer.validated_data['longitude']
        request.user.save(update_fields=['latitude', 'longitude'])
        return Response({'message': 'Coordonnees GPS mises a jour.'})

    @extend_schema(request=FCMTokenSerializer, responses={200: OpenApiResponse(description='Token FCM enregistre.')})
    @action(detail=False, methods=['post'], url_path='me/fcm-token')
    def update_fcm_token(self, request):
        serializer = FCMTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.fcm = serializer.validated_data['fcm_token']
        request.user.save(update_fields=['fcm'])
        return Response({'message': 'Token FCM mis a jour.'})

    @extend_schema(request=ParentChildRequestSerializer, responses={201: OpenApiResponse(description='Demande creee.')})
    @action(detail=False, methods=['post'], url_path='parent-child/request')
    def send_child_request(self, request):
        if not request.user.is_parent:
            return Response({'error': 'Seuls les comptes parents peuvent envoyer une demande.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ParentChildRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data['child_identifier'].strip()
        child = User.objects.filter(Q(email__iexact=identifier) | Q(username=identifier)).first()
        if child is None:
            return Response({'error': 'Utilisateur introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        if child == request.user:
            return Response({'error': 'Vous ne pouvez pas vous ajouter vous-meme.'}, status=status.HTTP_400_BAD_REQUEST)
        relation, _ = ParentChildRelation.objects.get_or_create(parent=request.user, child=child, defaults={'status': 'PENDING'})
        if relation.status == 'ACCEPTED':
            return Response({'error': 'Cet enfant est deja rattache a ce compte.'}, status=status.HTTP_400_BAD_REQUEST)
        if relation.status == 'REJECTED':
            relation.status = 'PENDING'
            relation.save(update_fields=['status'])
        if child.fcm:
            send_fcm_notification(fcm_token=child.fcm, title='Demande de rattachement parent', body=f'{request.user.get_full_name() or request.user.username} souhaite vous ajouter comme enfant.', data={'type': 'PARENT_REQUEST', 'relation_id': str(relation.id)})
        return Response({'message': 'Demande de rattachement envoyee.', 'relation_id': relation.id}, status=status.HTTP_201_CREATED)

    @extend_schema(request=ParentChildResponseSerializer, responses={200: OpenApiResponse(description='Demande traitee.')})
    @action(detail=False, methods=['post'], url_path='parent-child/respond')
    def respond_to_parent_request(self, request):
        serializer = ParentChildResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            relation = ParentChildRelation.objects.get(id=serializer.validated_data['relation_id'], child=request.user, status='PENDING')
        except ParentChildRelation.DoesNotExist:
            return Response({'error': 'Demande introuvable ou deja traitee.'}, status=status.HTTP_404_NOT_FOUND)
        if serializer.validated_data['action'] == 'accept':
            relation.status = 'ACCEPTED'
            relation.save(update_fields=['status'])
            parent_profile, _ = ParentProfile.objects.get_or_create(user=relation.parent)
            parent_profile.children.add(request.user)
            return Response({'message': 'Rattachement accepte.'})
        relation.status = 'REJECTED'
        relation.save(update_fields=['status'])
        return Response({'message': 'Rattachement refuse.'})

    @extend_schema(request=TutorDocumentUploadSerializer, responses={200: OpenApiResponse(description='Documents soumis.')})
    @action(detail=False, methods=['post'], url_path='me/tutor-documents')
    def upload_tutor_documents(self, request):
        if not request.user.is_teacher:
            return Response({'error': 'Reserve aux comptes tuteurs.'}, status=status.HTTP_403_FORBIDDEN)
        tutor_profile, _ = TutorProfile.objects.get_or_create(user=request.user)
        serializer = TutorDocumentUploadSerializer(tutor_profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Documents soumis. Votre compte est en cours de verification.'})

    @extend_schema(responses={200: OpenApiResponse(description='Compte desactive.')})
    @action(detail=False, methods=['delete'], url_path='me')
    def delete_account(self, request):
        user = request.user
        user.is_active = False
        user.fcm = None
        user.latitude = None
        user.longitude = None
        user.save(update_fields=['is_active', 'fcm', 'latitude', 'longitude'])
        for token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=token)
        return Response({'message': 'Votre compte a ete desactive et vos sessions ont ete supprimees.'})

    @extend_schema(responses={200: OpenApiResponse(description='Sessions fermees.')})
    @action(detail=False, methods=['post'], url_path='logout-all')
    def logout_all_devices(self, request):
        for token in OutstandingToken.objects.filter(user=request.user):
            BlacklistedToken.objects.get_or_create(token=token)
        return Response({'message': 'Toutes vos sessions actives ont ete fermees.'})

    @extend_schema(summary='Trouver des mentors a proximite', parameters=[OpenApiParameter('radius', type=float, description='Rayon en km. Defaut: 10.'), OpenApiParameter('lat', type=float, description='Latitude de reference optionnelle.'), OpenApiParameter('lng', type=float, description='Longitude de reference optionnelle.')], responses={200: NearbyTutorSerializer(many=True)})
    @action(detail=False, methods=['get'], url_path='nearby-tutors')
    def get_nearby_tutors(self, request):
        try:
            latitude = float(request.query_params.get('lat', request.user.latitude))
            longitude = float(request.query_params.get('lng', request.user.longitude))
            radius = float(request.query_params.get('radius', 10))
        except (TypeError, ValueError):
            return Response({'error': 'Les parametres lat, lng et radius doivent etre numeriques.'}, status=status.HTTP_400_BAD_REQUEST)
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180 or radius < 0:
            return Response({'error': 'Les coordonnees ou le rayon sont invalides.'}, status=status.HTTP_400_BAD_REQUEST)
        tutors = TutorProfile.objects.select_related('user').filter(user__is_teacher=True, user__is_active=True, user__latitude__isnull=False, user__longitude__isnull=False).exclude(user=request.user)
        nearby_tutors = []
        for tutor in tutors:
            distance = haversine_distance(latitude, longitude, float(tutor.user.latitude), float(tutor.user.longitude))
            if distance <= radius:
                tutor.distance_km = distance
                nearby_tutors.append(tutor)
        nearby_tutors.sort(key=lambda tutor: tutor.distance_km)
        return Response(NearbyTutorSerializer(nearby_tutors, many=True).data)
