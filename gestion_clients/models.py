from django.db import models

class Client(models.Model):
    
    nom_client = models.CharField(max_length=255, null=False, blank=False)
    domaine = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField()
    
    class Meta:
        verbose_name = ("client")
        verbose_name_plural = ("clients")
        
    def __str__(self):
         return self.nom_client
 