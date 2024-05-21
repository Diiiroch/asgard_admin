from django.db import models
from consultant.models import Consultant
# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class EventConge(models.Model):
    
    consultant = models.ForeignKey(Consultant, null=True, default=None,  on_delete=models.CASCADE, db_constraint=False)
    type = models.CharField(max_length=50, choices=[
        ('congé payé', 'Congé payé'),
        ('congé non payé', 'Congé non payé'),
        ('RTT', 'RTT'),
    ], default='congé payé')
    start = models.DateTimeField()
    end = models.DateTimeField()
    def serialize(self):
        return {
            'id': self.id,
            'type': self.type,
            'start': self.start.strftime("%Y-%m-%d"),
            'end': self.end.strftime("%Y-%m-%d"),
        }
