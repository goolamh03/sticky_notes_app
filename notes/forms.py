"""
Forms for the Sticky Notes application.

This module contains Django forms used for user registration,
profile management, and creating and updating sticky notes.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, StickyNote


class RegistrationForm(UserCreationForm):
    """Form used to register new user accounts.

        Extends Django's built-in UserCreationForm by adding a
        required email field. The form collects username,
        email address, and password information needed to
        create a new user account for the Sticky Notes
        application.

    Attributes:
        email (EmailField): Required email address for the
        user being registered.
    """

    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        """Configuration options for the RegistrationForm.

            Specifies the User model used by the form and defines the fields that are displayed and processed during user
            registration.

        Attributes:
            model (User): Django User model associated with the form.
            fields (tuple): User fields included in the registration form.
        """

        model = User
        fields = ("username", "email", "first_name", "last_name")


class StickyNoteForm(forms.ModelForm):
    """Form used to create and update sticky notes.

        Provides input fields for entering and editing the title
        and content of a sticky note. The form is based on the
        StickyNote model and customizes the content field to use
        a multi-line text area for improved usability.

    Attributes:
        Meta (class): Defines the model, fields, and widgets
        used by the form.
    """

    class Meta:
        """Configuration options for the form.

        Defines the model and fields used by the form.
        """

        model = StickyNote
        fields = ("title", "content")
        widgets = {
            "content": forms.Textarea(attrs={"rows": 8}),
        }


class UserProfileForm(forms.ModelForm):
    """Form used to update a user's account information.

        Provides fields for managing basic user details, including
        first name, last name, and email address. This form is used
        as part of the profile management functionality in the
        Sticky Notes application.

    Attributes:
        Meta (class): Defines the model and fields used
        by the form.
    """

    class Meta:
        """Metadata configuration for the UserProfileForm.

        Specifies the Django User model associated with the form and defines the user fields that can be viewed and updated through the profile management interface.

        Attributes:
            model (User): The Django authentication user model used by the form.
            fields (tuple): The user fields exposed for editing, including first name, last name, and email address.
        """

        model = User
        fields = ("first_name", "last_name", "email")


class ProfileForm(forms.ModelForm):
    """Form used to manage extended user profile information.

        Provides fields for updating profile-specific details that
        are not stored in Django's built-in User model, such as
        phone number and biography. This form is used as part of
        the profile management functionality in the Sticky Notes
        application.

    Attributes:
        Meta (class): Defines the model, fields, and widgets
        used by the form.
    """

    class Meta:
        """Configuration options for the ProfileForm.

        Specifies the Profile model, editable profile fields, and custom widgets used to render form inputs.

        Attributes:
            model (Profile): Profile model associated with the form.
            fields (tuple): Profile fields available for editing.
            widgets (dict): Custom widgets used to render profile form fields in the user interface.
        """

        model = Profile
        fields = ("phone_number", "bio")
        widgets = {"bio": forms.Textarea(attrs={"rows": 5})}
