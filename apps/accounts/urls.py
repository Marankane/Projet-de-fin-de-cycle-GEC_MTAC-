from django.urls import path
from . import views
app_name = 'accounts'
urlpatterns = [
    path('info-projet/', views.InfoProjetView.as_view(), name='info_projet'),
    path('connexion/', views.ConnexionView.as_view(), name='connexion'),
    path('deconnexion/', views.DeconnexionView.as_view(), name='deconnexion'),
    path('profil/', views.ProfilView.as_view(), name='profil'),
    path('utilisateurs/', views.ListeUtilisateursView.as_view(), name='liste_utilisateurs'),
    path('utilisateurs/creer/', views.CreerUtilisateurView.as_view(), name='creer_utilisateur'),
    path('utilisateurs/<int:pk>/modifier/', views.ModifierUtilisateurView.as_view(), name='modifier_utilisateur'),
    path('utilisateurs/<int:pk>/toggle/', views.ToggleUtilisateurView.as_view(), name='toggle_utilisateur'),
    path('reinitialisation/', views.DemandeReinitView.as_view(), name='demande_reinit'),
    path('reinitialisation/<str:token>/', views.ReinitMDPView.as_view(), name='reinit_mdp'),
]
