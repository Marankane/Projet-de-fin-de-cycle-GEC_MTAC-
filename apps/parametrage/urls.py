from django.urls import path
from . import views
app_name = 'parametrage'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('types/creer/', views.TypeCreateView.as_view(), name='creer_type'),
    path('types/<int:pk>/', views.TypeUpdateView.as_view(), name='modifier_type'),
    path('statuts/creer/', views.StatutCreateView.as_view(), name='creer_statut'),
    path('statuts/<int:pk>/', views.StatutUpdateView.as_view(), name='modifier_statut'),
    path('priorites/creer/', views.PrioriteCreateView.as_view(), name='creer_priorite'),
    path('priorites/<int:pk>/', views.PrioriteUpdateView.as_view(), name='modifier_priorite'),
]
