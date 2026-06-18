from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views
router = DefaultRouter()
router.register(r'accounts/utilisateurs', api_views.UtilisateurViewSet, basename='api-utilisateur')
urlpatterns = [
    path('accounts/connexion/', api_views.ConnexionAPIView.as_view(), name='api-connexion'),
    path('accounts/moi/', api_views.MonProfilView.as_view(), name='api-moi'),
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='api-refresh'),
    path('', include(router.urls)),
]
