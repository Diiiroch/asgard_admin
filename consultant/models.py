from django.db import models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
import phonenumbers
from django.core.exceptions import ValidationError
# Create your models here.
from gestion_clients.models import Client



def validate_phone_number(value):
    try:
        parsed_number = phonenumbers.parse(value, None)
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError('Invalid phone number')
    except phonenumbers.phonenumberutil.NumberParseException:
        raise ValidationError('Invalid phone number')

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Nom = models.CharField(max_length=20, blank=True, default=None)
    Prenom = models.CharField(max_length=20, blank=True, default=None)
    date_de_naissance = models.DateField(null=True, blank=True, default=None)
    genre = models.CharField(
        max_length=6,
        choices=[('HOMME','HOMME'),('FEMALE','FEMALE')]
    )
    email = models.EmailField(blank=True, null=True, default=None)
    tel = models.CharField(max_length=20, validators=[validate_phone_number], blank=True, default=None)
    def __str__(self):
        return self.user.username


class Consultant(models.Model):
    
    id = models.AutoField(primary_key=True)
    utilisateur = models.ForeignKey(User, null=True, default=None,on_delete=models.CASCADE, db_constraint=False)
    clients = models.ManyToManyField(Client)
    tjm = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Taux journalier moyen


    class Meta:
        verbose_name = ("consultant")
        verbose_name_plural = ("consultants")

    def __str__(self):
         return self.utilisateur.username


class Mission(models.Model):
    
    consultant = models.ForeignKey(Consultant, null=True, default=None,  on_delete=models.CASCADE, db_constraint=False)
    date_de_debut = models.DateField()
    date_de_fin = models.DateField()
    intitule = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True, default=None)
    client_concerne = models.ForeignKey(Client, null=True, default=None,  on_delete=models.CASCADE, db_constraint=False)

    
    class Meta:
        verbose_name = ("mission")
        verbose_name_plural = ("missions")
    
    def __str__(self):
        return self.intitule

class Contrat(models.Model):
    
    titulaire = models.ForeignKey(Consultant, null=True, default=None, on_delete=models.CASCADE, db_constraint=False)
    debut_contrat = models.DateField()
    fin_contrat = models.DateField()
    fichier = models.FileField()
    
    
    class Meta:
         verbose_name = ("contrat")
         verbose_name_plural = ("contrats")
        
    def __str__(self):
          return f'Contrat de {self.titulaire.utilisateur.username}'

class Projet(models.Model):
    
    code_projet = models.CharField(max_length=255, null=False, blank=False)
    intitule = models.CharField(max_length=255, null=False, blank=False)
    consultant = models.ForeignKey(Consultant, null=True, default=None,  on_delete=models.CASCADE, db_constraint=False)
    client_concerne = models.ForeignKey(Client, null=True, default=None,  on_delete=models.CASCADE, db_constraint=False)
    date_de_debut = models.DateField()
    date_de_fin = models.DateField()
    description = models.TextField(null=True, blank=True, default=None)
   
    
    class Meta:
        verbose_name = ("projet")
        verbose_name_plural = ("projets")    
    def __str__(self):
        return self.intitule

class TimeSheet(models.Model):
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    date = models.DateField()
    hours_worked = models.FloatField()  # Nombre d'heures travaillées (1 pour une journée, 0.5 pour une demi-journée, etc.)