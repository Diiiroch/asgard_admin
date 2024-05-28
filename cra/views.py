import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Events, Invoice, ValidationTable
from consultant.models import Projet, Consultant
from django.utils import timezone
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from django.template.loader import render_to_string
from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt
import logging
from decimal import Decimal
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
import calendar
import json
from django.contrib.auth.decorators import login_required, user_passes_test




def is_in_rh_group(user):
    return user.groups.filter(name='RH').exists()

@login_required
@require_POST
@user_passes_test(is_in_rh_group)
def validate_table(request):
    data = json.loads(request.body)
    validated = data.get('validated', False)
    validation_table = ValidationTable.objects.filter(validated=not validated).first()
    if validation_table:
        validation_table.validated = validated
        validation_table.save()
        return JsonResponse({'status': 'success', 'validated': validation_table.validated})
    return JsonResponse({'status': 'error'}, status=400)
logger = logging.getLogger(__name__)

class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = ['codeprojet', 'duration', 'start', 'end']

def index(request):  
    consultants = Consultant.objects.all()
    all_events = Events.objects.all()
    projets = Projet.objects.all()
    context = {
        "events": all_events,
        'projets': projets,
        'consultants': consultants
    }
    return render(request, 'cra/index.html', context)

def get_all_project_code(request):
    data = list(Projet.objects.values())
    return JsonResponse(data, safe=False)

def my_view(request):
    consultants = Consultant.objects.all()
    projets = Projet.objects.all()
    context = {
        'projets': projets,
        'consultants': consultants
    }
    return render(request, 'base.html', context)

def all_events(request):
    if request.method == 'GET' and request.is_ajax():
        events = Events.objects.all()
        events_data = [
            {
                'id': event.id,
                'title': f"{event.duration:.1f}",
                'start': event.start.isoformat(),
                'end': event.end.isoformat(),
                'codeprojet': event.codeprojet.code_projet,
                'duration': event.duration
            }
            for event in events
        ]
        return JsonResponse(events_data, safe=False)
    else:
        return JsonResponse({'error': 'Requête invalide'}, status=400)

@csrf_exempt
def update_event(request):
    if request.method == 'POST':
        try:
            logger.info("Requête POST reçue.")
            logger.info("Données de la requête : %s", request.POST)

            event_id = request.POST.get('event-id')
            duration = request.POST.get('duration')
            codeprojet = request.POST.get('codeprojet')

            if not event_id or not duration or not codeprojet:
                logger.error("Données invalides : event-id=%s, duration=%s, codeprojet=%s", event_id, duration, codeprojet)
                return JsonResponse({'error': 'Invalid data'}, status=400)

            try:
                event = Events.objects.get(id=event_id)
            except Events.DoesNotExist:
                logger.error("Événement introuvable : id=%s", event_id)
                return JsonResponse({'error': 'Event not found'}, status=404)

            try:
                projet = Projet.objects.get(id=codeprojet)
            except Projet.DoesNotExist:
                logger.error("Projet introuvable : id=%s", codeprojet)
                return JsonResponse({'error': 'Project not found'}, status=404)

            event.duration = float(duration)
            event.codeprojet = projet
            event.save()

            logger.info("Événement mis à jour avec succès : %s", event)
            return JsonResponse({'success': 'Event updated successfully'})
        except ValueError as e:
            logger.error("Erreur de validation : %s", str(e))
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            logger.error("Erreur inconnue : %s", str(e), exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)
    else:
        logger.error("Méthode de requête non valide : %s", request.method)
        return JsonResponse({'error': 'Invalid request method'}, status=405)

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
            
            # Ajouter l'événement pour le dernier jour (date de fin)
            event = Events(codeprojet_id=codeprojet_id, duration=duration, start=end, end=end)
            if not event.is_valid_event_duration():
                return JsonResponse({'error': 'La durée de l\'événement dépasse 1 heure pour ce jour'}, status=400)
            event.save()

            # Mettre à jour le modèle ValidationTable
            transfer_events(start.month, start.year)

            return JsonResponse({'success': 'Événement ajouté avec succès'}, status=201)
        else:
            return JsonResponse({'error': 'Tous les paramètres nécessaires n\'ont pas été fournis'}, status=400)
    else:
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def create_invoice(request, consultant_id):
    consultant = get_object_or_404(Consultant, pk=consultant_id)
    invoice = Invoice(consultant=consultant)
    invoice.calculate_prices()
    return redirect('invoice_detail', pk=invoice.pk)

def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    price_ht = invoice.price_ht
    tva = price_ht * Decimal(0.2)
    price_ttc = price_ht + tva
    tjm = invoice.tjm
    context = {
        'invoice': invoice,
        'price_ht': price_ht,
        'tva': tva,
        'price_ttc': price_ttc,
        'tjm': tjm
    }
    return render(request, 'cra/invoice_detail.html', context)

def event_table(request, mois, annee):
    user_is_rh = request.user.groups.filter(name='RH').exists()

    # Transférer les événements du modèle Events au modèle ValidationTable
    transfer_events(mois, annee)
    
    # Récupérer les événements du nouveau modèle ValidationTable
    consultant = get_object_or_404(Consultant, utilisateur=request.user)
    validation_table = ValidationTable.objects.filter(events__start__month=mois, events__start__year=annee).first()
    all_events = validation_table.events.all() if validation_table else Events.objects.none()
    
    # Créer une liste de tous les jours du mois
    _, num_days_in_month = calendar.monthrange(annee, mois)
    all_days = list(range(1, num_days_in_month + 1))
    
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
        'consultant_id': consultant.id,
        "current_month": current_month,
        "user_is_rh": user_is_rh,
        "num_days_in_month": num_days_in_month,
        "total_duration": total_duration,
        "validated": validation_table.validated if validation_table else False
    }

    # Rendre le template HTML avec le contexte
    return render(request, 'cra/event_table.html', context)

def transfer_events(mois, annee):
    existing_events = Events.objects.filter(start__month=mois, start__year=annee)
    if existing_events.exists():
        validation_table, created = ValidationTable.objects.get_or_create(
            validated=False,
        )
        validation_table.events.set(existing_events)
        validation_table.save()


