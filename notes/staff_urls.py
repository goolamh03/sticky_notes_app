"""
URL patterns for administrator functionality.

This module defines the URL routes used by staff members
to access administrative features such as user management,
system monitoring, and note administration.
"""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.staff_dashboard, name="staff_dashboard"),
    path("users/", views.staff_users, name="staff_users"),
    path(
        "users/<int:user_id>/deactivate/",
        views.staff_deactivate_user,
        name="staff_deactivate_user",
    ),
    path("notes/", views.staff_all_notes, name="staff_all_notes"),
]
