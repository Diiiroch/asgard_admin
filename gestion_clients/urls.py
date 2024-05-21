from django.urls import path
from . import views

urlpatterns = [
    path('', views.client_view, name='liste_clients'),
    # Ajoutez d'autres URL au besoin
]