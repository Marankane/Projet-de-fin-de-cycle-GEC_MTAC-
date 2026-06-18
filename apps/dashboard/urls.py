from django.urls import path
from .views import AccueilView
app_name = 'dashboard'
urlpatterns = [path('', AccueilView.as_view(), name='accueil')]
