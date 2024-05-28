from django.db import models
from consultant.models import Projet, Consultant
from django.db.models import Q
from decimal import Decimal

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

class Invoice(models.Model):
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE)
    event_table_sum = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tjm = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_prices(self):
        # Obtenez les projets du consultant
        projects = Projet.objects.filter(consultant=self.consultant)
        # Obtenez tous les événements associés à ces projets
        events = Events.objects.filter(codeprojet__in=projects)
        self.event_table_sum = Decimal(sum(event.duration for event in events) or 0)  # Convertir en Decimal
        self.tjm = self.consultant.tjm or Decimal(0)
        self.price_ht = self.event_table_sum * self.tjm
        self.price_ttc = self.price_ht * Decimal(1.2)  # TVA de 20%
        self.save()

    def __str__(self):
        return f"Invoice for {self.consultant.utilisateur.username} on {self.created_at}"


