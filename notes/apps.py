"""
Application configuration for the Sticky Notes application.

This module contains the Django application configuration
responsible for initializing application components and
registering signal handlers during startup.
"""
from django.apps import AppConfig


class NotesConfig(AppConfig):
    """Configuration class for the Notes application.

        This class defines application-specific settings for the
        Sticky Notes Django app, including the default primary key
        field type and the application name used by Django.

    Attributes:
        default_auto_field (str): Specifies the default type of
        primary key field for models that do not explicitly
        define one.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "notes"

    def ready(self):
        """Perform application startup initialization.

        Imports the application's signal handlers when the Django
        application is loaded. This ensures that signal receivers
        are registered and available for handling events such as
        user creation and profile creation.

        Returns:
            None
        """
        import notes.signals  # noqa: F401
