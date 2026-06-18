from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Priorite, StatutCourrier, TypeCourrier

class TypeSerializer(serializers.ModelSerializer):
    class Meta: model=TypeCourrier; fields='__all__'
class StatutSerializer(serializers.ModelSerializer):
    class Meta: model=StatutCourrier; fields='__all__'
class PrioriteSerializer(serializers.ModelSerializer):
    class Meta: model=Priorite; fields='__all__'

class TypeVS(viewsets.ReadOnlyModelViewSet):
    queryset=TypeCourrier.objects.filter(actif=True).order_by('ordre')
    serializer_class=TypeSerializer; permission_classes=[IsAuthenticated]
class StatutVS(viewsets.ReadOnlyModelViewSet):
    queryset=StatutCourrier.objects.all().order_by('ordre')
    serializer_class=StatutSerializer; permission_classes=[IsAuthenticated]
class PrioriteVS(viewsets.ReadOnlyModelViewSet):
    queryset=Priorite.objects.all().order_by('ordre')
    serializer_class=PrioriteSerializer; permission_classes=[IsAuthenticated]

router = DefaultRouter()
router.register(r'types', TypeVS, basename='api-type')
router.register(r'statuts', StatutVS, basename='api-statut')
router.register(r'priorites', PrioriteVS, basename='api-priorite')
urlpatterns = [path('', include(router.urls))]
