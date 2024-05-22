from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import EventConge
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from consultant.models import Consultant
from django.contrib.auth.models import User
from collections import defaultdict
from datetime import datetime



@login_required
@csrf_exempt
def save_event(request):
    if request.method == 'POST':
        user = request.user
        try:
            consultant = Consultant.objects.get(utilisateur=user)
        except Consultant.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Consultant not found'}, status=404)

        event_type = request.POST.get('type')
        start = request.POST.get('start')
        end = request.POST.get('end')

        if not all([event_type, start, end]):
            return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)

        try:
            event = EventConge.objects.create(type=event_type, start=start, end=end, consultant=consultant)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def fetch_events(request):
    events = EventConge.objects.all()
    event_list = []
    for event in events:
        event_list.append({
            'id': event.id,
            'title': event.type,
            'start': event.start.strftime("%Y-%m-%d"),
            'end': event.end.strftime("%Y-%m-%d"),
            'type': event.type,
        })
    return JsonResponse(event_list, safe=False)
def conge_view(request):
    return render(request, 'conge/base_conge.html' )




@login_required
def event_summary(request):
    # Récupérer l'utilisateur connecté
    user = request.user

    # Récupérer tous les événements de congé
    events = EventConge.objects.filter(consultant__utilisateur=user)

    # Organiser les événements par type et trier les dates
    events_by_type = defaultdict(list)
    for event in events:
        events_by_type[event.type].append(event)
    
    # Calculer la période cohérente pour chaque type de congé
    periods_by_type = {}
    for event_type, events in events_by_type.items():
        sorted_events = sorted(events, key=lambda e: e.start)
        start_date = sorted_events[0].start
        end_date = sorted_events[-1].end
        periods_by_type[event_type] = {
            'start': start_date.strftime("%Y-%m-%d"),
            'end': end_date.strftime("%Y-%m-%d")
        }

    context = {
        'periods_by_type': periods_by_type,
        'username': user.username
    }
    
    return render(request, 'conge/event_summary.html', context)


def update_event_conge(request):
    if request.method == 'POST':
        event_id = request.POST.get('event-id')
        event_type = request.POST.get('event-type')
        
        if not event_id:
            return JsonResponse({'status': 'error', 'message': 'Event ID is missing'})

        try:
            event = EventConge.objects.get(id=event_id)
            event.type = event_type
            event.save()
            return JsonResponse({'status': 'success'})
        except EventConge.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
@csrf_exempt
def delete_all_events(request):
    if request.method == 'POST':
        try:
            EventConge.objects.filter(consultant__utilisateur=request.user).delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})