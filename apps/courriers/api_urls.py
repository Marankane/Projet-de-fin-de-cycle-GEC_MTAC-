from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import api_views
router = DefaultRouter()
router.register(r'courriers', api_views.CourrierViewSet, basename='api-courrier')
router.register(r'expediteurs', api_views.ExpediteurViewSet, basename='api-expediteur')
urlpatterns = [path('', include(router.urls))]
