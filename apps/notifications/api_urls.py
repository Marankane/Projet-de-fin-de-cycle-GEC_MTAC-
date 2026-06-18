from django.urls import path
from . import api_views

app_name = 'notifications'

urlpatterns = [
    path('notifications/', api_views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:id>/', api_views.NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/count/', api_views.notification_count, name='notification-count'),
    path('notifications/unread/', api_views.unread_notifications, name='unread-notifications'),
    path('notifications/<int:notification_id>/read/', api_views.mark_as_read, name='mark-as-read'),
    path('notifications/read-all/', api_views.mark_all_as_read, name='mark-all-as-read'),
    path('api/notifications/', api_views.NotificationListView.as_view(), name='notification-list-legacy'),
    path('api/notifications/count/', api_views.notification_count, name='notification-count-legacy'),
    path('api/notifications/unread/', api_views.unread_notifications, name='unread-notifications-legacy'),
    path('api/notifications/<int:notification_id>/read/', api_views.mark_as_read, name='mark-as-read-legacy'),
]
