# courses/views/mixins.py
"""Mixins d'API réutilisables pour le Course Builder."""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


class ReorderMixin:
    """Ajoute ``POST {prefix}reorder/`` pour réordonner des éléments pédagogiques.

    Le corps attendu est ``{"order": [3, 1, 2]}`` : les identifiants dans
    l'ordre pédagogique souhaité (spec §5, importance du champ ``order``).
    """
    #: callable(request) -> QuerySet, par défaut ``self.get_queryset()``.
    reorder_queryset = None

    @action(detail=False, methods=['post'], url_path='reorder')
    def reorder(self, request):
        order = request.data.get('order')
        if not isinstance(order, list) or not order:
            raise ValidationError({'order': 'Fournissez une liste d’identifiants dans l’ordre souhaité.'})

        queryset = self.reorder_queryset(request) if self.reorder_queryset else self.get_queryset()
        by_id = {str(item.id): item for item in queryset}
        updated = 0
        for position, item_id in enumerate(order, start=1):
            item = by_id.get(str(item_id))
            if item is None:
                continue
            item.order = position
            item.save(update_fields=['order'])
            updated += 1

        if not updated:
            raise ValidationError({'order': 'Aucun élément correspondant n’a été trouvé.'})
        return Response({'message': f'{updated} élément(s) réordonné(s).'}, status=status.HTTP_200_OK)
