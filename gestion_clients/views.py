import os
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages


from consultant.models import Consultant

@login_required
def client_view(request):
    if request.user.is_authenticated:
        user = request.user
        consultants = Consultant.objects.all()
        clients_associated = []
        
        # Itérer sur chaque consultant pour récupérer les clients associés
        for consultant_instance in consultants:
            clients = consultant_instance.clients.all()
            clients_associated.extend(clients)
            
        return render(request, 'gestions_clients/list.html', {'clients_associated': clients_associated,  'consultants': consultants } )
    else:
        
        return redirect('admin:login')