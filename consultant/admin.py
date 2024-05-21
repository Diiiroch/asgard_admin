from django.contrib import admin
from .models import Account, Contrat, Mission, Consultant, Projet
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import AbstractUser
from gestion_clients.models import Client



from django.db import models




class AccountInLine(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'Accounts'
    
class CustomizedUserAdmin (UserAdmin):
     inlines = (AccountInLine, )
    


admin.site.unregister(User)
admin.site.register(User, CustomizedUserAdmin)

admin.site.register(Account)
admin.site.register(Client)
admin.site.register(Contrat)
admin.site.register(Projet)
admin.site.register(Consultant)
admin.site.register(Mission)


# Register your models here.
