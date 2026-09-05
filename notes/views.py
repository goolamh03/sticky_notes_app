"""
Views for the Sticky Notes application.

This module contains view functions that handle user
authentication, profile management, sticky note CRUD
operations, search functionality, archiving, restoration,
and administrator features.
"""
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    ProfileForm,
    RegistrationForm,
    StickyNoteForm,
    UserProfileForm,
)
from .models import AuditLog, StickyNote


def home(request):
    """Redirect authenticated users to the notes dashboard and unauthenticated users to the login page.

    Args:
        request (_type_): Django HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects the user to either the
        notes list page or the login page.
    """
    if request.user.is_authenticated:
        return redirect("notes:list")
    return redirect("login")


def register(request):
    """Register a new user account and redirect authenticated users to the notes dashboard.

        If the user is already authenticated, the user is redirected to the notes list page. Otherwise, the registration form is displayed and processed.

    Args:
        request (_type_): Django HTTP request object.

    Returns:
        HttpResponse: Rendered registration page when displaying the form or validation errors.
        HttpResponseRedirect: Redirect to the notes dashboard after successful registration or if the user is already
        authenticated.
    """
    if request.user.is_authenticated:
        return redirect("notes:list")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        AuditLog.objects.create(user=user, action="User registered")
        login(request, user)
        messages.success(request, "Your account was created successfully.")
        return redirect("notes:list")
    return render(request, "registration/register.html", {"form": form})


@login_required
def profile(request):
    """Display and update the authenticated user's profile information.

        This view allows a logged-in user to view and modify account
        details and profile information. When valid form data is
        submitted, the user and profile records are updated within
        a database transaction and an audit log entry is created.

    Args:
        request (_type_): Django HTTP request object containing
        GET or POST data.

    Returns:
        HttpResponse: Rendered profile page displaying the user and
        profile forms.
        HttpResponseRedirect: Redirect to the profile page after a
        successful profile update.
    """
    user_form = UserProfileForm(request.POST or None, instance=request.user)
    profile_form = ProfileForm(
        request.POST or None,
        instance=request.user.profile,
    )
    if request.method == "POST":
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
                AuditLog.objects.create(
                    user=request.user,
                    action="Profile updated",
                )
            messages.success(request, "Your profile was updated.")
            return redirect("profile")
    context = {"user_form": user_form, "profile_form": profile_form}
    return render(request, "registration/profile.html", context)


@login_required
def note_list(request):
    """Display and search active sticky notes belonging to the authenticated user.

        Retrieves all non-archived sticky notes owned by the current user. If a search query is provided, the notes are filtered by matching the title or content. The resulting notes and search query are rendered in the notes list template.

    Args:
        request (HttpRequest): Django HTTP request object containing optional search parameters.

    Returns:
        HttpResponse: Rendered notes list page displaying the user's active sticky notes and any search results.
    """
    query = request.GET.get("q", "").strip()
    notes = StickyNote.objects.filter(owner=request.user, archived=False)
    if query:
        notes = notes.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    return render(
        request,
        "notes/note_list.html",
        {"notes": notes, "query": query},
    )


@login_required
def note_detail(request, pk):
    """Display the details of a specific sticky note owned by the authenticated user.

        Retrieves a sticky note using its primary key and verifies that it belongs to the currently logged-in user. If the note does not exist or is not owned by the user, a 404 error is returned.

    Args:
        request (HttpRequest): Django HTTP request object.
        pk (int): Primary key of the sticky note to retrieve.

    Returns:
        HttpResponse: Rendered note detail page displaying the selected sticky note.
    """
    note = get_object_or_404(StickyNote, pk=pk, owner=request.user)
    return render(request, "notes/note_detail.html", {"note": note})


@login_required
def note_create(request):
    """Create a new sticky note for the authenticated user.

    Args:
        request (HttpRequest): Django HTTP request object.

    Returns:
        HttpResponse: Rendered note form or redirect response.
    """
    form = StickyNoteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        note = form.save(commit=False)
        note.owner = request.user
        note.save()
        AuditLog.objects.create(
            user=request.user,
            action="Note created",
            details=f"Note ID {note.pk}",
        )
        messages.success(request, "Sticky note created.")
        return redirect(note)
    return render(
        request,
        "notes/note_form.html",
        {"form": form, "heading": "Create sticky note"},
    )


@login_required
def note_update(request, pk):
    """Update an existing sticky note owned by the authenticated user.

        Retrieves the specified sticky note, displays a pre-populated
        form containing the current note details, and processes updates
        submitted by the user. After a successful update, an audit log
        entry is created, a success message is displayed, and the user
        is redirected to the updated note.

    Args:
        request (HttpRequest): Django HTTP request object containing
        GET or POST data.
        pk (int): Primary key of the sticky note to update.

    Returns:
        HttpResponse: Rendered note update form when displaying the
        page or when form validation fails.
        HttpResponseRedirect: Redirect to the updated note after a
        successful update.
    """
    note = get_object_or_404(StickyNote, pk=pk, owner=request.user)
    form = StickyNoteForm(request.POST or None, instance=note)
    if request.method == "POST" and form.is_valid():
        form.save()
        AuditLog.objects.create(
            user=request.user,
            action="Note updated",
            details=f"Note ID {note.pk}",
        )
        messages.success(request, "Sticky note updated.")
        return redirect(note)
    return render(
        request,
        "notes/note_form.html",
        {"form": form, "heading": "Update sticky note"},
    )


@login_required
def note_delete(request, pk):
    """Delete an existing sticky note owned by the authenticated user.

        Retrieves the specified sticky note and removes it from the database.
        An audit log entry is created upon successful deletion, a success
        message is displayed, and the user is redirected to the note list.

    Args:
        request (HttpRequest): Django HTTP request object containing
        POST data.
        pk (int): Primary key of the sticky note to delete.

    Returns:
        HttpResponse: Rendered delete confirmation page or redirect response.
    """
    note = get_object_or_404(StickyNote, pk=pk, owner=request.user)
    if request.method == "POST":
        note_id = note.pk
        note.delete()
        AuditLog.objects.create(
            user=request.user,
            action="Note deleted",
            details=f"Note ID {note_id}",
        )
        messages.success(request, "Sticky note deleted.")
        return redirect("notes:list")
    return render(request, "notes/note_confirm_delete.html", {"note": note})


@login_required
def note_archive(request, pk):
    """Archive a sticky note owned by the authenticated user.

        This view processes a POST request to archive an existing
        sticky note. The note is marked as archived, an audit log
        entry is created, a success message is displayed, and the
        user is redirected to the notes list page. Access is denied
        if the request method is not POST.

    Args:
        request (HttpRequest): Django HTTP request object.
        pk (int): Primary key of the sticky note to archive.

    Returns:
        HttpResponseForbidden: Returned when the request method
        is not POST.
        HttpResponseRedirect: Redirects to the notes list page
        after the note has been successfully archived.
    """
    if request.method != "POST":
        return HttpResponseForbidden("Archive requires a POST request.")
    note = get_object_or_404(StickyNote, pk=pk, owner=request.user)
    note.archived = True
    note.save(update_fields=["archived", "updated_at"])
    AuditLog.objects.create(
        user=request.user,
        action="Note archived",
        details=f"Note ID {note.pk}",
    )
    messages.success(request, "Sticky note archived.")
    return redirect("notes:list")


@login_required
def archived_notes(request):
    """Display all archived sticky notes belonging to the authenticated user.

        Retrieves archived sticky notes owned by the currently logged-in
        user and renders them on the archived notes page. This view allows
        users to review and restore previously archived notes.

    Args:
        request (HttpRequest): Django HTTP request object.

    Returns:
        HttpResponse: Rendered archived notes page displaying the
        user's archived sticky notes.
    """
    notes = StickyNote.objects.filter(owner=request.user, archived=True)
    return render(request, "notes/archived_list.html", {"notes": notes})


@login_required
def note_restore(request, pk):
    """Restore an archived sticky note owned by the authenticated user.

        This view processes a POST request to restore an existing
        archived sticky note. The note is marked as not archived, an audit log
        entry is created, a success message is displayed, and the
        user is redirected to the notes list page. Access is denied
        if the request method is not POST.

    Args:
        request (HttpRequest): Django HTTP request object.
        pk (int): Primary key of the sticky note to restore.

    Returns:
        HttpResponseForbidden: Returned when the request method
        is not POST.
        HttpResponseRedirect: Redirects to the notes list page
        after the note has been successfully restored.
    """
    if request.method != "POST":
        return HttpResponseForbidden("Restore requires a POST request.")
    note = get_object_or_404(
        StickyNote,
        pk=pk,
        owner=request.user,
        archived=True,
    )
    note.archived = False
    note.save(update_fields=["archived", "updated_at"])
    AuditLog.objects.create(
        user=request.user,
        action="Note restored",
        details=f"Note ID {note.pk}",
    )
    messages.success(request, "Sticky note restored.")
    return redirect("notes:list")


def staff_required(view_func):
    """Restrict access to authenticated staff users.

        This decorator ensures that a user is logged in and has
        staff privileges before allowing access to the decorated
        view. If the authenticated user is not a staff member,
        an HTTP 403 Forbidden response is returned.

    Args:
        view_func (callable): The view function to be protected.

    Returns:
        callable: Wrapped view function that enforces
        staff-only access.
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("Administrator access required.")
        return view_func(request, *args, **kwargs)

    return wrapper


@staff_required
def staff_dashboard(request):
    """Restrict access to staff users only.

        This decorator ensures that a user is authenticated and has
        staff privileges before allowing access to the decorated view.
        If the user is not a staff member, an HTTP 403 Forbidden
        response is returned.

    Args:
        view_func (callable): The view function to be protected.

    Returns:
        callable: Wrapped view function that enforces staff-only
        access control.
    """
    context = {
        "user_count": User.objects.count(),
        "active_user_count": User.objects.filter(is_active=True).count(),
        "note_count": StickyNote.objects.count(),
        "archived_note_count": StickyNote.objects.filter(
            archived=True
        ).count(),
        "recent_logs": AuditLog.objects.select_related("user")[:20],
    }
    return render(request, "staff/monitoring.html", context)


@staff_required
def staff_users(request):
    """Display a list of all registered users for administrator management.

        Retrieves all user accounts from the database, ordered by
        username, and renders them on the user management page. This
        view is restricted to authenticated staff members through the
        staff_required decorator.

    Args:
        request (HttpRequest): Django HTTP request object.

    Returns:
        HttpResponse: Rendered user management page displaying all
        registered users.
    """
    users = User.objects.order_by("username")
    return render(request, "staff/user_list.html", {"users": users})


@staff_required
def staff_deactivate_user(request, user_id):
    """Deactivate a user account.

        Retrieves the specified user account and allows an administrator
        to deactivate it. Administrators cannot deactivate their own
        accounts. When a user is successfully deactivated, the account's
        active status is set to False, an audit log entry is created,
        and a success message is displayed.

    Args:
        request (HttpRequest): Django HTTP request object.
        user_id (int): Primary key of the user account to be
        deactivated.

    Returns:
        HttpResponse: Rendered confirmation page requesting
        deactivation approval.
        HttpResponseRedirect: Redirect to the user management page
        after processing the deactivation request.
    """
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        if user == request.user:
            messages.error(request, "You cannot deactivate your own account.")
        else:
            user.is_active = False
            user.save(update_fields=["is_active"])
            AuditLog.objects.create(
                user=request.user,
                action="User deactivated",
                details=f"User ID {user.pk}",
            )
            messages.success(request, "User account deactivated.")
        return redirect("staff_users")
    return render(request, "staff/deactivate_user.html", {"target": user})


@staff_required
def staff_all_notes(request):
    """Display all sticky notes in the system.

        Retrieves all sticky notes from the database, including their
        associated owners, and displays them on the administrator
        notes management page. This view is restricted to staff users
        and provides administrators with a system-wide overview of
        user-created notes.

    Args:
        request (HttpRequest): Django HTTP request object.

    Returns:
        HttpResponse: Rendered administrator notes page displaying
        all sticky notes and their owners.
    """
    notes = StickyNote.objects.select_related("owner").all()
    return render(request, "staff/all_notes.html", {"notes": notes})
