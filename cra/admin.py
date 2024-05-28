from django.contrib import admin
from .models import Events, Invoice, ValidationTable


admin.site.register(Events)
admin.site.register(Invoice)
admin.site.register(ValidationTable)
# Register your models here.
