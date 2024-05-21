import datetime
from django.shortcuts import render
from django.http import JsonResponse 
from .models import Events 
from consultant.models import Projet
import re
from django.utils import timezone
import datetime
from django import forms
from django.http import HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models import Sum
from django.template.loader import render_to_string
from django.shortcuts import render,  get_object_or_404
from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt


from datetime import datetime, timedelta
import calendar

from datetime import datetime
from django.http import HttpResponse



class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = ['codeprojet', 'duration', 'start', 'end']


def index(request):  
    all_events = Events.objects.all()
    projets = Projet.objects.all()
    context = {
        "events":all_events,
        'projets': projets
        
    }
    return render(request,'cra/index.html',context)

    
@csrf_exempt
def update_event(request):
    if request.method == 'POST':
        event_id = request.POST.get('id')
        duration = request.POST.get('duration')
        codeprojet_id = request.POST.get('codeprojet')

        try:
            event = get_object_or_404(Events, pk=event_id)
            event.duration = float(duration)
            event.codeprojet_id = codeprojet_id
            event.save()
            return JsonResponse({'success': 'Événement mis à jour avec succès'})
        except Events.DoesNotExist:
            return JsonResponse({'error': 'Événement non trouvé'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Requête invalide'}, status=400)
def get_all_project_code(request):
    data = list(Projet.objects.values())  # Query your model and convert to a list of dictionaries
    print(JsonResponse(data, safe=False))
    return JsonResponse(data, safe=False)

def my_view(request):
    projets = Projet.objects.all()
    context = {
        'projets': projets,
    }
    return render(request, 'base.html', context)

def all_events(request):
    if request.method == 'GET' and request.is_ajax():
        # Récupérer la durée spécifiée dans la requête
        duration_filter = float(request.GET.get('duration', 1.0))  # Par défaut, 1 heure
        tolerance = 0.1
        # Filtrer les événements en fonction de la durée
        filtered_events = Events.objects.filter(
            Q(duration=duration_filter) |  # Correspondance exacte pour duration_filter
            Q(duration=0.5) |  # Inclure les événements avec une durée de 0,5
            Q(duration=0.25) |  # Inclure les événements avec une durée de 0,25
            Q(duration__gt=duration_filter - tolerance, duration__lt=duration_filter + tolerance)  # Plage de tolérance
          )

        # Créer une liste des événements filtrés au format JSON
        events_data = []
        for event in filtered_events:
            formatted_duration = f"{event.duration:.1f}"  # Formater à 2 décimales
            code_projet = event.codeprojet.code_projet
            events_data.append({
                'title': formatted_duration , # Afficher la durée de l'événement
                'start': event.start.isoformat(),  # Date de début de l'événement au format ISO 8601
                'end': event.end.isoformat(),  # Date de fin de l'événement au format ISO 8601
                'codeprojet': code_projet,  # Code du projet associé à l'événement
            })
        
        # Renvoyer les données des événements filtrés au format JSON
        return JsonResponse(events_data, safe=False)
    else:
        # Si la requête n'est pas AJAX ou n'est pas GET, renvoyer une erreur
        return JsonResponse({'error': 'Requête invalide'}, status=400)


def add_event(request):
    if request.method == 'GET':
        codeprojet_id = request.GET.get('codeprojet')
        duration = float(request.GET.get('duration'))
        start = datetime.strptime(request.GET.get('start'), '%Y-%m-%d')
        end = datetime.strptime(request.GET.get('end'), '%Y-%m-%d')

        if codeprojet_id and duration and start and end:
            # Vérifier si la somme totale des durées des événements pour ce jour dépasse 1 heure
            events_on_date = Events.objects.filter(start__date=start.date())
            total_duration_on_date = sum(event.duration for event in events_on_date)
            if total_duration_on_date + duration > 1.0:
                return JsonResponse({'error': 'La durée de l\'événement dépasse 1 heure pour ce jour'}, status=400)

            # Créer une instance d'Events avec les objets datetime pour chaque jour
            current_date = start
            while current_date < end:
                event = Events(codeprojet_id=codeprojet_id, duration=duration, start=current_date, end=current_date)
                # Vérifier si la durée de l'événement est valide
                if not event.is_valid_event_duration():
                    return JsonResponse({'error': 'La durée de l\'événement dépasse 1 heure pour ce jour'}, status=400)
                # Sauvegarder l'événement pour ce jour
                event.save()
                # Passer au jour suivant
                current_date += timedelta(days=1)

            return JsonResponse({'success': 'Événement ajouté avec succès'}, status=201)
        else:
            return JsonResponse({'error': 'Tous les paramètres nécessaires n\'ont pas été fournis'}, status=400)
    else:
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)




def event_table(request, mois, annee):
    # Récupérer tous les événements de la base de données
    all_events = Events.objects.filter(start__month=mois, start__year=annee)

    # Créer une liste de tous les jours du mois
    ##_, num_days_in_month = calendar.monthrange(datetime.now().year, datetime.now().month)
    _, num_days_in_month = calendar.monthrange(annee, mois)
    all_days = list(range(1, num_days_in_month + 1))
    print(all_days)
    
    # Récupérer le nom de l'utilisateur connecté
    user_name = request.user.get_username()

    # Récupérer le mois actuel
    current_month = calendar.month_name[mois]

    # Calculer la somme totale des durées pour afficher dans la case "Total Durée"
    total_duration = sum(event.duration for event in all_events)

    # Créer le dictionnaire de contexte à passer au template
    context = {
        "events": all_events,
        "all_days": all_days,
        "user_name": user_name,
        "current_month": current_month,
        "num_days_in_month": num_days_in_month,
        "total_duration": total_duration,
    }

    # Rendre le template HTML avec le contexte
   
    return render(request, 'cra/event_table.html', context)

