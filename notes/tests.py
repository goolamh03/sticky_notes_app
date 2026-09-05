"""
Unit tests for the Sticky Notes application.

This module contains test cases that verify note CRUD
operations, search functionality, access control,
archiving, restoration, and administrator features.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import StickyNote


class NoteCrudTests(TestCase):
    """Test CRUD functionality for sticky notes.

    This test case verifies that authenticated users can create, view,
    update, and delete their own notes while ensuring that access controls
    prevent unauthorized users from modifying notes they do not own.

    The test environment creates two users and authenticates the primary
    user before each test method is executed.
    """

    def setUp(self):
        """Set up test data and authenticate the test client.

        Creates two user accounts for testing ownership and access control
        scenarios, then logs in the primary test user for authenticated
        requests during test execution.
        """
        self.user = User.objects.create_user(
            username="owner",
            password="StrongPass123!",
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)

    def test_create_note_assigns_logged_in_owner(self):
        """Verify that a newly created note is assigned to the logged-in user.

        Ensures that the note owner is automatically set to the authenticated
        user who submits the create request and that the user is redirected
        to the note's detail page after successful creation.
        """
        response = self.client.post(
            reverse("notes:create"),
            {"title": "Test", "content": "Content"},
        )
        note = StickyNote.objects.get(title="Test")
        self.assertEqual(note.owner, self.user)
        self.assertRedirects(response, note.get_absolute_url())

    def test_list_shows_only_active_owned_notes(self):
        """Verify that the note list displays only the authenticated user's active notes.

        Ensures that archived notes and notes owned by other users are excluded from the notes list view, while active notes belonging to the logged-in user are displayed.
        """
        StickyNote.objects.create(
            owner=self.user,
            title="Visible",
            content="Own active note",
        )
        StickyNote.objects.create(
            owner=self.user,
            title="Archived",
            content="Own archived note",
            archived=True,
        )
        StickyNote.objects.create(
            owner=self.other_user,
            title="Private",
            content="Another user's note",
        )
        response = self.client.get(reverse("notes:list"))
        self.assertContains(response, "Visible")
        self.assertNotContains(response, "Own archived note")
        self.assertNotContains(response, "Private")

    def test_search_checks_title_and_content(self):
        """Verify that note search matches both titles and content.

        Ensures that a note is returned in the search results when the
        search query matches text contained within the note's content,
        even if the query does not appear in the title.
        """
        StickyNote.objects.create(
            owner=self.user,
            title="Django",
            content="Framework notes",
        )
        response = self.client.get(reverse("notes:list"), {"q": "framework"})
        self.assertContains(response, "Django")

    def test_user_cannot_update_another_users_note(self):
        """Verify that a user cannot update a note owned by another user.

        Ensures that attempting to access the update view for a note that
        does not belong to the authenticated user results in a 404 Not Found
        response, preventing unauthorized access.
        """
        note = StickyNote.objects.create(
            owner=self.other_user,
            title="Protected",
            content="Private",
        )
        response = self.client.get(reverse("notes:update", args=[note.pk]))
        self.assertEqual(response.status_code, 404)

    def test_archive_and_restore_note(self):
        """Verify that a note can be archived and later restored.

        Ensures that the archive operation marks the note as archived and
        that the restore operation returns the note to an active state by
        updating the archived flag accordingly.
        """
        note = StickyNote.objects.create(
            owner=self.user,
            title="Archive me",
            content="Content",
        )
        self.client.post(reverse("notes:archive", args=[note.pk]))
        note.refresh_from_db()
        self.assertTrue(note.archived)
        self.client.post(reverse("notes:restore", args=[note.pk]))
        note.refresh_from_db()
        self.assertFalse(note.archived)

    def test_archived_notes_view(self):
        """
        Verify that archived notes appear in the archived notes view.

        Ensures that archived notes belonging to the logged-in
        user are displayed correctly.
        """
        StickyNote.objects.create(
            owner=self.user,
            title="Archived Note",
            content="Archived Content",
            archived=True,
        )

        response = self.client.get(
            reverse("notes:archived")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Archived Note")


class StaffViewTests(TestCase):
    """Test staff-only views and administrative functionality.

        These tests verify that users with staff privileges can access
        administrative views and perform management actions, while
        non-staff users are restricted from accessing protected resources.

    Args:
        TestCase (django.test.TestCase): Base Django test case class
        providing database isolation, a test client, and assertion
        methods for testing application behavior.
    """

    def setUp(self):
        """Create test user accounts for administrator and member roles.

        Initializes sample users used throughout the staff-related
        test cases. A staff user is created to simulate administrator
        access, while a standard user is created to verify access
        restrictions and authorization behavior.

        Args:
            self (StaffViewTests): Current test case instance.

        Returns:
            None
        """
        self.staff = User.objects.create_user(
            username="admin_user",
            password="StrongPass123!",
            is_staff=True,
        )
        self.member = User.objects.create_user(
            username="member",
            password="StrongPass123!",
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="StrongPass123!",
        )

    def test_staff_can_view_monitoring_dashboard(self):
        """Verify that staff users can access the monitoring dashboard.

        Ensures that an authenticated user with staff privileges can
        successfully view the monitoring dashboard and receives an
        HTTP 200 OK response.
        """
        self.client.force_login(self.staff)
        response = self.client.get(reverse("staff_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_non_staff_is_forbidden(self):
        """Verify that non-staff users cannot access the monitoring dashboard.

        Ensures that an authenticated user without staff privileges is
        denied access to the monitoring dashboard and receives an
        HTTP 403 Forbidden response.
        """
        self.client.force_login(self.member)
        response = self.client.get(reverse("staff_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_note_detail_view(self):
        """
        Verify that a user can view the detail page of their own note.

        Ensures that the note detail view returns an HTTP 200 response
        and displays the note content for the owner.
        """
        note = StickyNote.objects.create(
            owner=self.member,
            title="Detail Test",
            content="Detail Content",
        )

        self.client.force_login(self.member)
        response = self.client.get(
            reverse("notes:detail", args=[note.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detail Content")

    def test_note_update_view(self):
        """
        Verify that a user can update one of their own notes.

        Ensures that submitting valid update data modifies the note
        record in the database successfully.
        """
        self.client.force_login(self.member)

        note = StickyNote.objects.create(
            owner=self.member,
            title="Original",
            content="Original Content",
        )

        response = self.client.post(
            reverse("notes:update", args=[note.pk]),
            {
                "title": "Updated",
                "content": "Updated Content",
            },
        )

        note.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(note.title, "Updated")
        self.assertEqual(note.content, "Updated Content")

    def test_note_create_page_loads(self):
        """
        Verify that the note creation page loads successfully.

        Ensures that authenticated users can access the create
        note form.
        """
        self.client.force_login(self.member)

        response = self.client.get(reverse("notes:create"))

        self.assertEqual(response.status_code, 200)

    def test_user_cannot_view_other_users_note(self):
        """
        Verify that users cannot view notes they do not own.

        Ensures that attempting to access another user's note
        returns a 404 response.
        """
        note = StickyNote.objects.create(
            owner=self.other_user,
            title="Private Note",
            content="Secret",
        )

        self.client.force_login(self.member)
        response = self.client.get(
            reverse("notes:detail", args=[note.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_staff_can_view_user_list(self):
        """
        Verify that staff users can access the user management list.

        Ensures that the staff users page loads successfully.
        """
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse("staff_users")
        )

        self.assertEqual(response.status_code, 200)

    def test_staff_can_deactivate_user(self):
        """
        Verify that staff users can deactivate a member account.

        Ensures that the selected user becomes inactive after
        the staff action is performed.
        """
        self.client.force_login(self.staff)

        self.client.post(
            reverse(
                "staff_deactivate_user",
                args=[self.member.id]
            )
        )

        self.member.refresh_from_db()

        self.assertFalse(self.member.is_active)

    def test_staff_can_view_all_notes(self):
        """
        Verify that staff users can access the all notes view.

        Ensures that the administrative notes page loads
        successfully.
        """
        StickyNote.objects.create(
            owner=self.member,
            title="User Note",
            content="Test",
        )

        self.client.force_login(self.staff)

        response = self.client.get(
            reverse("staff_all_notes")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User Note")

    def test_member_cannot_view_user_list(self):
        """
        Verify that non-staff users cannot access the user list.

        Ensures that a 403 Forbidden response is returned.
        """
        self.client.force_login(self.member)

        response = self.client.get(
            reverse("staff_users")
        )

        self.assertEqual(response.status_code, 403)
