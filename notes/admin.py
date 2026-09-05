"""
Admin configuration for the Sticky Notes application.

This module contains Django admin registrations and
customizations for application models.
"""
from django.contrib import admin

from .models import AuditLog, Profile, StickyNote


@admin.register(StickyNote)
class StickyNoteAdmin(admin.ModelAdmin):
    """Admin configuration for the StickyNote model.

    Defines how sticky notes are displayed, filtered, and
    searched within the Django administration interface.
    Administrators can view note ownership, archive status,
    and modification history to efficiently manage notes.

    Attributes:
        list_display (tuple): Fields displayed in the admin
        list view.
        list_filter (tuple): Fields available for filtering
        sticky notes.
        search_fields (tuple): Fields used when performing
        searches in the admin interface.
    """

    list_display = ("title", "owner", "archived", "updated_at")
    list_filter = ("archived", "created_at", "updated_at")
    search_fields = ("title", "content", "owner__username")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin configuration for the Profile model.

        Provides search functionality for user profile records
        within the Django administration interface. Administrators
        can search profiles using associated usernames and email
        addresses to quickly locate and manage user information.

    Attributes:
        search_fields (tuple): Fields used to search profile
        records in the admin interface.
    """

    search_fields = ("user__username", "user__email")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin configuration for the AuditLog model.

        Provides administrators with the ability to view, filter,
        and search audit log records within the Django administration
        interface. Audit logs record user and system activities,
        supporting monitoring, troubleshooting, and compliance
        requirements.

    Attributes:
        list_display (tuple): Fields displayed in the audit log
        list view.
        list_filter (tuple): Fields available for filtering audit
        log records.
        search_fields (tuple): Fields used to search audit log
        entries in the admin interface.
    """

    list_display = ("action", "user", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("action", "details", "user__username")
