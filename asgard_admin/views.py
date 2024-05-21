import os
from django.http import FileResponse
from django.conf import settings
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages

from consultant.models import Consultant, Contrat, Mission, Projet

from gestion_clients.models import Client



def client_list_view(request):
    client = Client.objects.all()
    return render(request, 'dashboard/list_client.html', {
        'client':client 
    })


def client_details_view(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    return render(request,'dashboard/client_details.html', {
        'client': client
    } )


def profil_user(request):
    return render(request, 'dashboard/profil.html')
    

    


@login_required
def Accueil(request):
    if request.user.is_authenticated:
        user = request.user
        # Vérifier si un consultant est associé à l'utilisateur
        consultants = Consultant.objects.all()
        # Si aucun consultant n'est trouvé, vous pouvez rediriger l'utilisateur vers une page d'erreur
        # Ou afficher un message approprié, par exemple :
        # return render(request, 'error.html', {'message': 'Aucun consultant associé à cet utilisateur.'})
        
        clients = Client.objects.all() 
        
        
        
        # Récupérer les contrats 
        contrats_associated = Contrat.objects.all()
        # Récupérer les missions  
        mission_associated = Mission.objects.all()
        
        
        return render(request, 'dashboard/home.html', { 'clients': clients, 
                                                       'contrats': contrats_associated,
                                                       'missions': mission_associated, 
                                                       'consultants': consultants,
                                                       'user' : user
                                                       
                                                       } )    
    else:
        
        return redirect('admin:login')
    
def logout_user(request):
    logout(request)       
    messages.success(request,("Vous êtes déconnécté !! "))
    return redirect('Accueil')






    
