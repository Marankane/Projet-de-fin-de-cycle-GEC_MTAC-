from django.urls import path
from . import views, api
app_name = 'courriers'
urlpatterns = [
    path('', views.ListeCourrierView.as_view(), name='liste'),
    path('registre/', views.RegistreEnregistrementView.as_view(), name='registre'),
    path('enregistrement/', views.EnregistrementView.as_view(), name='enregistrement'),
    path('api/process-document/', api.process_document, name='process_document'),
    path('<int:pk>/', views.DetailCourrierView.as_view(), name='detail'),
    path('<int:pk>/fichier-transmission/', views.FichierTransmissionView.as_view(), name='fichier_transmission'),
    path('<int:pk>/modifier/', views.ModifierCourrierView.as_view(), name='modifier'),
    path('<int:pk>/dispatcher/', views.DispatchView.as_view(), name='dispatcher'),
    path('<int:pk>/dispatcher/', views.DispatchView.as_view(), name='dispatch'),
    path('bulk-dispatch/', views.BulkDispatchView.as_view(), name='bulk_dispatch'),
    path('<int:pk>/instruction/', views.InstructionView.as_view(), name='instruction'),
    path('<int:pk>/valider/', views.ValiderView.as_view(), name='valider'),
    path('<int:pk>/cloturer/', views.CloturerView.as_view(), name='cloturer'),
    path('<int:pk>/pieces-jointes/', views.AjouterPJView.as_view(), name='ajouter_pj'),
    path('<int:pk>/pieces-jointes/<int:pj_pk>/supprimer/', views.SupprimerPJView.as_view(), name='supprimer_pj'),
    path('<int:pk>/liens/', views.AjouterLienView.as_view(), name='ajouter_lien'),
    path('expediteurs/creer/', views.ExpéditeurCreateView.as_view(), name='creer_expediteur'),
    path('destinataires/creer/', views.DestinataireCreateView.as_view(), name='creer_destinataire'),
]
