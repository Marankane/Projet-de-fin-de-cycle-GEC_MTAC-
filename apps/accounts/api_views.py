from rest_framework import serializers, status, viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from core.permissions import EstAdmin
from .models import Utilisateur

class UtilisateurSerializer(serializers.ModelSerializer):
    nom_complet = serializers.CharField(read_only=True)
    initiales = serializers.CharField(read_only=True)
    role_label = serializers.CharField(source='get_role_display', read_only=True)
    service_nom = serializers.CharField(source='service.nom', read_only=True, default=None)
    class Meta:
        model = Utilisateur
        fields = ['id','nom','prenom','nom_complet','initiales','email','role','role_label',
                  'service','service_nom','telephone','is_active','peut_dispatcher','peut_valider','peut_voir_tout']

class ConnexionAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        mdp = request.data.get('mot_de_passe') or request.data.get('password')
        user = authenticate(request, username=email, password=mdp)
        if not user or not user.is_active:
            return Response({'detail': 'Identifiants invalides.'}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token), 'refresh': str(refresh), 'utilisateur': UtilisateurSerializer(user).data})

class MonProfilView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request): return Response(UtilisateurSerializer(request.user).data)
    def patch(self, request):
        ser = UtilisateurSerializer(request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True); ser.save()
        return Response(UtilisateurSerializer(request.user).data)

class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.select_related('service').order_by('nom')
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAuthenticated, EstAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nom', 'prenom', 'email']
