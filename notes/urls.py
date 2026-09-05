"""
URL configuration for the Sticky Notes application.

This module defines URL patterns that map incoming
requests to the appropriate note-related views.
"""
from django.urls import path

from . import views

app_name = "notes"

urlpatterns = [
    path("", views.note_list, name="list"),
    path("create/", views.note_create, name="create"),
    path("archived/", views.archived_notes, name="archived"),
    path("<int:pk>/", views.note_detail, name="detail"),
    path("<int:pk>/update/", views.note_update, name="update"),
    path("<int:pk>/delete/", views.note_delete, name="delete"),
    path("<int:pk>/archive/", views.note_archive, name="archive"),
    path("<int:pk>/restore/", views.note_restore, name="restore"),
]
