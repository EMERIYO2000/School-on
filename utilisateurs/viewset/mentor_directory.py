
# utilisateurs/viewset/mentor_directory.py
"""Annuaire public des mentors (spec §27, §28 et §47)."""
from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from ..models import MentorReport, TutorProfile
from ..serializers.mentor_serializers import (
    MentorDirectorySerializer,
    MentorPublicSerializer,
    MentorReportSerializer,
)
from ..utils.geo_utils import haversine_distance
from bookings.models import BookingReview
from bookings.serializers import BookingReviewSerializer


class MentorDirectoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Annuaire public des mentors (spec §27, §28 et §47).

    - ``GET /api/mentors/``               : mentors vérifiés (filtres ``city``, ``domain``,
      ``search``, ``ordering``, ``verified_only``, ``nearby`` + ``lat``/``lng``/``radius``) ;
    - ``GET /api/mentors/{id}/``          : profil public (aucune donnée sensible) ;
    - ``POST /api/mentors/{id}/report/``  : signalement d'un mentor (spec §32).
    """
    serializer_class = MentorPublicSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = TutorProfile.objects.select_related('user').prefetch_related('user__mentor_skills')
        params = self.request.query_params

        # Par défaut, seuls les mentors vérifiés sont visibles publiquement.
        if params.get('verified_only', 'true').lower() != 'false':
            queryset = queryset.filter(mentor_status='VERIFIED', is_verified=True)
        if params.get('city'):
            queryset = queryset.filter(Q(city__icontains=params['city']) | Q(public_location__icontains=params['city']))
        if params.get('domain'):
            queryset = queryset.filter(
                Q(user__mentor_skills__domain__icontains=params['domain'])
                | Q(user__mentor_skills__specialization__icontains=params['domain'])
            ).distinct()
        if params.get('available') == 'true':
            queryset = queryset.filter(is_available=True)
        if params.get('search'):
            term = params['search']
            queryset = queryset.filter(
                Q(user__first_name__icontains=term)
                | Q(user__last_name__icontains=term)
                | Q(user__username__icontains=term)
                | Q(headline__icontains=term)
                | Q(bio__icontains=term)
            ).distinct()
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return MentorDirectorySerializer
        return MentorPublicSerializer

    def list(self, request, *args, **kwargs):
        """Liste filtrée, avec option de tri par distance (spec §17)."""
        queryset = self.filter_queryset(self.get_queryset())
        params = request.query_params

        ordering = params.get('ordering', '-is_verified')
        allowed = {'-is_verified', 'hourly_rate', '-hourly_rate', 'years_of_experience', '-years_of_experience', 'user__username'}
        queryset = queryset.order_by(ordering if ordering in allowed else '-is_verified')

        if params.get('nearby') == 'true':
            try:
                latitude = float(params.get('lat', request.user.latitude if request.user.is_authenticated else None))
                longitude = float(params.get('lng', request.user.longitude if request.user.is_authenticated else None))
            except (TypeError, ValueError):
                raise ValidationError({'detail': 'Les paramètres lat et lng doivent être numériques.'})
            radius = float(params.get('radius', 20))

            nearby = []
            for profile in queryset:
                if profile.user.latitude is None or profile.user.longitude is None:
                    continue
                distance = haversine_distance(
                    latitude, longitude, float(profile.user.latitude), float(profile.user.longitude)
                )
                if distance <= radius:
                    profile.distance_km = round(distance, 2)
                    nearby.append(profile)
            nearby.sort(key=lambda profile: profile.distance_km)

            serializer = MentorDirectorySerializer(nearby, many=True, context={'request': request})
            return Response({'results': serializer.data, 'count': len(nearby)})

        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def report(self, request, pk=None):
        """Signale un mentor (spec §32) — un utilisateur ne peut pas se signaler lui-même."""
        profile = self.get_object()
        if profile.user_id == request.user.id:
            raise ValidationError({'detail': 'Vous ne pouvez pas vous signaler vous-même.'})
        serializer = MentorReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report, created = MentorReport.objects.get_or_create(
            mentor=profile.user,
            reporter=request.user,
            reason=serializer.validated_data['reason'],
            defaults={'details': serializer.validated_data.get('details', '')},
        )
        if not created:
            raise ValidationError({'detail': 'Vous avez déjà signalé ce mentor pour ce motif.'})
        return Response(MentorReportSerializer(report).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'], url_path='reviews', permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def reviews(self, request, pk=None):
        """Avis créés uniquement après une réservation terminée."""
        profile = self.get_object()
        bookings = profile.tutor_bookings.filter(status='completed')
        if request.method == 'POST':
            booking_id = request.data.get('booking')
            booking = bookings.filter(id=booking_id, student=request.user).first()
            if booking is None:
                return Response({'detail': 'Un avis est possible uniquement après votre session terminée.'}, status=status.HTTP_400_BAD_REQUEST)
            if hasattr(booking, 'review'):
                return Response({'detail': 'Cette session a déjà reçu un avis.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = BookingReviewSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            review = serializer.save(booking=booking)
            return Response(BookingReviewSerializer(review).data, status=status.HTTP_201_CREATED)

        reviews = BookingReview.objects.filter(booking__in=bookings).select_related('booking__student')
        average = sum(item.rating for item in reviews) / reviews.count() if reviews.exists() else 0
        return Response({
            'mentor': profile.id,
            'sessions_completed': bookings.count(),
            'learners': bookings.values('student').distinct().count(),
            'average_rating': round(average, 1),
            'reviews': BookingReviewSerializer(reviews, many=True).data,
        })
