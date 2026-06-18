from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Case, When, Value, IntegerField, F
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = self.request.user.notifications.select_related('courrier__priorite').all()
        
        # Annotate with priority order
        qs = qs.annotate(
            priority_order=Case(
                # Urgent courriers first
                When(type='COURRIER_ASSIGNE', courrier__priorite__code__in=['URG', 'TRES_URG'], then=Value(0)),
                # Then by type priority
                When(type='COURRIER_ECHU', then=Value(1)),
                When(type='COURRIER_ASSIGNE', then=Value(2)),
                When(type='COURRIER_RETOURNE', then=Value(3)),
                When(type='RAPPEL', then=Value(4)),
                default=Value(5),
                output_field=IntegerField(),
            )
        ).order_by('priority_order', '-cree_le')
        
        return qs

class NotificationDetailView(generics.RetrieveAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return self.request.user.notifications.all()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, utilisateur=request.user)
    notification.lue = True
    notification.save()
    return Response({'status': 'ok', 'notification': NotificationSerializer(notification).data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_as_read(request):
    count = request.user.notifications.filter(lue=False).update(lue=True)
    return Response({'status': 'ok', 'updated': count})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_count(request):
    count = request.user.notifications.filter(lue=False).count()
    total = request.user.notifications.count()
    return Response({'count': count, 'total': total})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_notifications(request):
    """Retourne les notifications non lues avec détails, triées par priorité"""
    limit = request.query_params.get('limit', 10)
    
    notifications = request.user.notifications.filter(lue=False).select_related(
        'courrier__priorite', 'courrier__expediteur'
    ).annotate(
        priority_order=Case(
            When(type='COURRIER_ASSIGNE', courrier__priorite__code__in=['URG', 'TRES_URG'], then=Value(0)),
            When(type='COURRIER_ECHU', then=Value(1)),
            When(type='COURRIER_ASSIGNE', then=Value(2)),
            When(type='COURRIER_RETOURNE', then=Value(3)),
            When(type='RAPPEL', then=Value(4)),
            default=Value(5),
            output_field=IntegerField(),
        )
    ).order_by('priority_order', '-cree_le')[:int(limit)]
    
    data = []
    for notif in notifications:
        item = {
            'id': notif.id,
            'type': notif.type,
            'titre': notif.titre,
            'message': notif.message,
            'lien': notif.lien,
            'lue': notif.lue,
            'cree_le': notif.cree_le.isoformat(),
            'is_urgent': notif.type == 'COURRIER_ASSIGNE' and hasattr(notif, 'courrier') and notif.courrier and notif.courrier.priorite.code in ['URG', 'TRES_URG'],
        }
        if notif.courrier:
            item['courrier_numero'] = notif.courrier.numero
            item['courrier_objet'] = notif.courrier.objet[:60]
        data.append(item)
    
    return Response({
        'count': len(data),
        'notifications': data
    })