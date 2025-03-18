from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/new/', views.event_create, name='event_create'),
    path('event/<int:pk>/edit/', views.event_update, name='event_update'),
    path('event/<int:pk>/delete/', views.event_delete, name='event_delete'),


    path('sessions/', views.session_list, name='session_list'),
    path('events/<int:event_id>/sessions/new/', views.session_create, name='session_create'),
    path('session/<int:pk>/edit/', views.session_update, name='session_update'),
    path('sessions/<int:pk>/delete/', views.session_delete, name='session_delete'),

    path('speakers/', views.speaker_list, name='speaker_list'),
    path('speaker/<int:pk>/', views.speaker_detail, name='speaker_detail'),
    path('speaker/new/', views.speaker_create, name='speaker_create'),
    path('speaker/<int:pk>/edit/', views.speaker_edit, name='speaker_edit'),
    path('speaker/<int:pk>/delete/', views.speaker_delete, name='speaker_delete'),

    path('assign_speaker/<int:session_id>/', views.assign_speaker, name='assign_speaker'),

    path('events/optimized_schedule/', views.optimized_schedule_view, name='optimized_schedule'),

]