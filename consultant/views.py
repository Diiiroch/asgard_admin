import os
from django.http import FileResponse
from django.conf import settings
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages

from consultant.models import Consultant, Contrat, Mission, Projet

def consultant_list_view(request):
    consultant = Consultant.objects.all()
    return render(request, 'dashboard/list_consultant.html', {
        'consultant': consultant
    })
def contrat_list_view(request):
    contrat = Contrat.objects.all()
    return render(request, 'dashboard/list_contrat.html', {
        'contrats': contrat
    } )
    
def mission_view(request):
    missions = Mission.objects.all()
    return render(request, 'dashboard/mission.html', {
        'missions': missions
    })
def projet_view(request):
    projets = Projet.objects.all()
    return render(request, 'dashboard/list_projet.html', {
        'projets': projets
    })
def mission_details_view(request, mission_id):   
    missions = get_object_or_404(Mission, id=mission_id)
    return render(request, 'dashboard/mission_details.html', {
        'missions': missions
    })
def projet_details_view(request, projet_id):   
    projets = get_object_or_404(Projet, id=projet_id)
    return render(request, 'dashboard/projet_details.html', {
        'projets': projets
    })
def contrat_details_view(request, contrat_id):   
    contrats = get_object_or_404(Contrat, id=contrat_id)
    return render(request, 'dashboard/contrat_details.html', {
        'contrats': contrats
    })   
def download_contrat(request, contrat_id):
    contrat = get_object_or_404(Contrat, id=contrat_id)
    # Chemin complet du fichier
    filepath = os.path.join(settings.MEDIA_ROOT, str(contrat.fichier))
    # Ouvre le fichier et retourne une réponse de fichier
    return FileResponse(open(filepath, 'rb'), as_attachment=True)

def missions_clients(request, consultant_id):
    
    # Récupérer le consultant en fonction de l'identifiant
    
    

        consultant = get_object_or_404(Consultant, id=consultant_id)

    # Récupérer les missions associées à ce consultant
        missions = consultant.mission_set.all()
    
    # Créer une liste de clients associés à ces missions
        clients = set()
        for mission in missions:
            clients.add(mission.client_concerne)
    
    # Rendre le template avec les données nécessaires
        return render(request, 'dashboard/missions_clients.html', {
        'missions': missions,
        'clients': clients,
        'consultant': consultant, # Assurez-vous que consultant est bien défini ici
    })

