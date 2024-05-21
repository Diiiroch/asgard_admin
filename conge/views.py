from django.shortcuts import render
from django.http import JsonResponse
from .models import EventConge
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from consultant.models import Consultant
from django.contrib.auth.models import User



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
    if request.method == 'GET':
        events = EventConge.objects.all()
        serialized_events = [{'title': event.type, 'start': event.start, 'end': event.end, 'consultant': event.consultant.utilisateur.username} for event in events]
        return JsonResponse(serialized_events, safe=False)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
def conge_view(request):
    return render(request, 'conge/base_conge.html' )




def event_summary(request):
    # Récupérer l'utilisateur actuel
    user = request.user

    try:
        # Récupérer le consultant associé à l'utilisateur actuel
        consultant = Consultant.objects.get(utilisateur=user)
    except Consultant.DoesNotExist:
        # Si le consultant n'est pas trouvé, retourner une réponse d'erreur
        return JsonResponse({'status': 'error', 'message': 'Consultant not found'}, status=404)
    
    # Récupérer les événements associés à ce consultant
    events = EventConge.objects.filter(consultant=consultant)
    
    event_summary = {}
    for event in events:
        if event.type not in event_summary:
            event_summary[event.type] = {'start': event.start, 'end': event.end}
        else:
            # Mettre à jour la date de début et la date de fin si nécessaire
            if event.start < event_summary[event.type]['start']:
                event_summary[event.type]['start'] = event.start
            if event.end > event_summary[event.type]['end']:
                event_summary[event.type]['end'] = event.end
    
    # Passer les événements au contexte de rendu
    return render(request, 'conge/event_summary.html', {'events': events, 'consultant':consultant, 'event_summary': event_summary})
