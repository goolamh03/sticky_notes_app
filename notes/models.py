"""
Database models for the Sticky Notes application.

This module defines the Profile, StickyNote, and AuditLog
models used to store user information, notes, and audit
events within the application.
"""
from django.conf import settings
from django.db import models
from django.urls import reverse


class Profile(models.Model):
    """Represents an extended user profile associated with a single user account.

        This model stores additional user information that is not included in the
        default Django User model. Each profile is linked to exactly one user and
        contains optional contact and biographical details.

    Attributes:
        user (User): A one-to-one relationship with the authenticated user.
        Deleting the user also deletes the associated profile.
        phone_number (str): An optional phone number for the user.
        bio (str): An optional biography or description about the user.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone_number = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        """Return a human-readable string representation of the profile.

        Returns:
            str: A string identifying the profile's associated user.
        """
        return f"Profile for {self.user.username}"


class StickyNote(models.Model):
    """Represents a sticky note created and owned by a user.

        Sticky notes allow users to save and manage personal notes within the
        application. Each note contains a title, content, timestamps for creation
        and modification, and an archive status used to hide notes from the active
        note list without permanently deleting them.

    Attributes:
        owner (User): The user who owns the note.
        title (str): The title of the note.
        content (str): The main body content of the note.
        created_at (datetime): The date and time the note was created.
        updated_at (datetime): The date and time the note was last modified.
        archived (bool): Indicates whether the note has been archived.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    title = models.CharField(max_length=120)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived = models.BooleanField(default=False)

    class Meta:
        """Configure model metadata for StickyNote.

        Notes are ordered by their most recently updated timestamp in descending order so that the latest modified notes appear first.
        """

        ordering = ["-updated_at"]

    def __str__(self):
        """Return the title of the sticky note.

        Returns:
            str: The note title used as its human-readable representation.
        """
        return self.title

    def get_absolute_url(self):
        """Return the canonical URL for this sticky note.

        Returns:
            str: The URL of the note detail page.
        """
        return reverse("notes:detail", kwargs={"pk": self.pk})


class AuditLog(models.Model):
    """Record user and system activities for auditing purposes.

        This model stores a history of actions performed within the application.
        Each log entry may be associated with a user and includes a description of the action, optional details, and the timestamp when the event occurred.

    Attributes:
        user (User | None): The user associated with the action, if available.
        action (str): A short description of the action performed.
        details (str): Additional information about the action.
        created_at (datetime): The date and time the log entry was created.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=80)
    details = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Configuration options for the AuditLog model.

        Defines the default ordering of audit log records so that the most recently created events are displayed first.

        Attributes:
            ordering (list): Sort audit log entries by creation date in descending order.
        """

        ordering = ["-created_at"]

    def __str__(self):
        """Return a human-readable representation of the audit log entry.

        Returns:
            str: A formatted string containing the action and timestamp of the audit log entry.
        """
        return f"{self.action} at {self.created_at:%Y-%m-%d %H:%M}"
