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
from django.urls import reverse

logger = logging.getLogger(__name__)

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

class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = ['codeprojet', 'duration', 'start', 'end']

@login_required
def index(request):  
    logger.info(f"User {request.user.username} accessed index.")
    if is_in_rh_group(request.user):
        logger.info(f"User {request.user.username} is in RH group, redirecting to liste_tableaux_a_valider.")
        return redirect(reverse('liste_tableaux_a_valider'))

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

@login_required
def my_view(request):
    logger.info(f"User {request.user.username} accessed my_view.")
    if is_in_rh_group(request.user):
        logger.info(f"User {request.user.username} is in RH group, redirecting to liste_tableaux_a_valider.")
        return redirect(reverse('liste_tableaux_a_valider'))

    consultants = Consultant.objects.all()
    projets = Projet.objects.all()
    context = {
        'projets': projets,
        'consultants': consultants
    }
    return render(request, 'cra/base.html', context)

@login_required
def liste_tableaux_a_valider(request):
    tableaux = ValidationTable.objects.filter(validated=False)
    context = {
        'tableaux': tableaux
    }
    return render(request, 'cra/liste_tableaux_a_valider.html', context)

def all_events(request):
    if request.method == 'GET' and request.is_ajax():
        consultant = get_object_or_404(Consultant, utilisateur=request.user)
        events = Events.objects.filter(consultant=consultant)
        
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
        duration = request.GET.get('duration')
        start = request.GET.get('start')
        end = request.GET.get('end')

        logger.debug(f'Reçu - codeprojet: {codeprojet_id}, duration: {duration}, start: {start}, end: {end}')

        if not (codeprojet_id and duration and start and end):
            logger.error('Tous les paramètres nécessaires n\'ont pas été fournis')
            return JsonResponse({'error': 'Tous les paramètres nécessaires n\'ont pas été fournis'}, status=400)

        try:
            duration = float(duration)
            start = datetime.strptime(start, '%Y-%m-%d')
            end = datetime.strptime(end, '%Y-%m-%d')
        except ValueError as e:
            logger.error(f'Erreur de format des données: {str(e)}')
            return JsonResponse({'error': f'Erreur de format des données: {str(e)}'}, status=400)

        consultant = get_object_or_404(Consultant, utilisateur=request.user)
        logger.debug(f'Consultant trouvé: {consultant}')

        events_on_date = Events.objects.filter(start__date=start.date(), consultant=consultant)
        total_duration_on_date = sum(event.duration for event in events_on_date)
        logger.debug(f'Durée totale des événements pour le {start.date()}: {total_duration_on_date}')

        if total_duration_on_date + duration > 1.0:
            logger.error('La durée de l\'événement dépasse 1 heure pour ce jour')
            return JsonResponse({'error': 'La durée de l\'événement dépasse 1 heure pour ce jour'}, status=400)

        current_date = start
        while current_date <= end:
            event = Events(
                codeprojet_id=codeprojet_id, 
                duration=duration, 
                start=current_date, 
                end=current_date, 
                consultant=consultant
            )
            try:
                if not event.is_valid_event_duration():
                    logger.error('La durée de l\'événement dépasse 1 heure pour ce jour')
                    return JsonResponse({'error': 'La durée de l\'événement dépasse 1 heure pour ce jour'}, status=400)
                event.save()
            except ValueError as e:
                logger.error(f'Erreur lors de l\'enregistrement de l\'événement: {str(e)}')
                return JsonResponse({'error': f'Erreur lors de l\'enregistrement de l\'événement: {str(e)}'}, status=400)
            current_date += timedelta(days=1)

        logger.debug('Événement ajouté avec succès')
        return JsonResponse({'success': 'Événement ajouté avec succès'}, status=201)
    else:
        logger.error('Méthode non autorisée')
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

@login_required
def event_table(request, mois, annee):
    user_is_rh = request.user.groups.filter(name='RH').exists()

    # Obtenez le consultant associé à l'utilisateur connecté
    consultant = get_object_or_404(Consultant, utilisateur=request.user)
    transfer_events(mois, annee, consultant)

    # Filtrez les événements par consultant
    validation_table = ValidationTable.objects.filter(consultant=consultant, events__start__month=mois, events__start__year=annee).first()
    all_events = validation_table.events.all() if validation_table else Events.objects.filter(consultant=consultant, start__month=mois, start__year=annee)

    _, num_days_in_month = calendar.monthrange(annee, mois)
    all_days = list(range(1, num_days_in_month + 1))

    user_name = request.user.get_username()
    current_month = calendar.month_name[mois]
    total_duration = sum(event.duration for event in all_events)

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

    return render(request, 'cra/event_table.html', context)

def transfer_events(mois, annee, consultant):
    existing_events = Events.objects.filter(start__month=mois, start__year=annee, consultant=consultant)
    if existing_events.exists():
        validation_table, created = ValidationTable.objects.get_or_create(
            consultant=consultant,
            validated=False,
        )
        validation_table.events.set(existing_events)
        validation_table.save()