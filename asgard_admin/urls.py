
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views as main_views
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from cra import views as cra_views
from consultant import views as consultant_view
from conge import views as conge_views

urlpatterns = [
    path('',main_views.Accueil, name='Accueil'),
    path('admin/', admin.site.urls), 

    path('logout_user/', main_views.logout_user, name='logout'),
    path('missions_clients/<int:consultant_id>/', consultant_view.missions_clients, name='missions_clients'),
    path('profil_user/', main_views.profil_user, name='profil'),
    path('mission/', consultant_view.mission_view, name='mission'),
    path('mission_details/<int:mission_id>/', consultant_view.mission_details_view, name='mission_details'),
    path('contrat_details/<int:contrat_id>/', consultant_view.contrat_details_view, name='contrat_details'),
    path('projet_details/<int:projet_id>/', consultant_view.projet_details_view, name='projet_details'),
    path('consultant_list/', consultant_view.consultant_list_view, name='consultant_list'),
    path('client_list/', main_views.client_list_view, name='client_list'),
    path('contrat_list/', consultant_view.contrat_list_view, name='contrat_list'),
    path('projet_list/', consultant_view.projet_view, name='projet_list'),
    path('client_details/<int:client_id>/', main_views.client_details_view, name='client_details'),
    path('ajouter_consultant/', RedirectView.as_view(url='/admin/consultant/consultant/add/'), name='ajouter_consultant'),
    path('modifier_consultant/', RedirectView.as_view(url='/admin/consultant/consultant/'), name='modifier_consultant'),
    path('ajouter_mission/', RedirectView.as_view(url='/admin/consultant/mission/add/'), name='ajouter_mission'),
    path('modifier_mission/', RedirectView.as_view(url='/admin/consultant/mission/'), name='modifier_mission'),
    path('ajouter_client/', RedirectView.as_view(url='/admin/gestion_clients/client/add/'), name='ajouter_client'),
    path('modifier_client/', RedirectView.as_view(url='/admin/gestion_clients/client/'), name='modifier_client'),
    path('ajouter_contrat/', RedirectView.as_view(url='/admin/consultant/contrat/add/'), name='ajouter_contrat'),
    path('modifier_contrat/', RedirectView.as_view(url='/admin/consultant/contrat/'), name='modifier_contrat'),
    path('contrat/<int:contrat_id>/download/', consultant_view.download_contrat, name='download_contrat'),
    path('ajouter_projet/', RedirectView.as_view(url='/admin/consultant/projet/add/'), name='ajouter_projet'),
    path('modifier_projet/', RedirectView.as_view(url='/admin/consultant/projet/'), name='modifier_projet'),
    path('cra/', cra_views.index, name='index_cra'),
    path('cra/all_events/', cra_views.all_events, name='all_events'),
    path('cra/all_projects/code',cra_views.get_all_project_code),
    path('cra/add_event', cra_views.add_event),
    path('event-table/<int:mois>/<int:annee>/', cra_views.event_table, name='event_table'),
    path('cra/update_event/', cra_views.update_event, name='update_event'),
    path('update_event_conge/', conge_views.update_event_conge, name='update_event_conge'),
    path('delete_all_events/', conge_views.delete_all_events, name='delete_all_events'),  # Ajouter cette ligne

    path('save_event/', conge_views.save_event, name="save_event"),
    path('conge/', conge_views.conge_view, name="conge_view"),
    path('fetch_events/', conge_views.fetch_events, name='fetch_events'),
    path('event-summary/', conge_views.event_summary, name='event_summary'),


  
       
   
    
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)