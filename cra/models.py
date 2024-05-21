from django.db import models
from consultant.models import Projet
from django.db.models import Q

class Events(models.Model):
    codeprojet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    duration = models.FloatField(choices=[(1, '1'), (0.5, '0.5'), (0.25, '0.25')], default=1)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def serialize(self):
        return {
            'id': self.id,
            'codeprojet': self.codeprojet.code_projet,
            'duration': self.duration,
            'start': self.start.strftime("%Y-%m-%d"),
            'end': self.end.strftime("%Y-%m-%d"),
        }

    def is_valid_event_duration(self):
        # Exclure l'événement en cours de modification de la validation
        events_on_date = Events.objects.filter(start__date=self.start.date()).exclude(Q(id=self.id))
        total_duration_on_date = sum(event.duration for event in events_on_date)
        
        return total_duration_on_date + self.duration <= 1.0

    def save(self, *args, **kwargs):
        if not self.is_valid_event_duration():
            raise ValueError("La durée totale des événements pour cette journée dépasse 1 heure.")
        super().save(*args, **kwargs)
    