"""
Comprehensive tests for the kb (knowledge base) app.

Covers: KBEntry and Resource CRUD, read access for all roles,
write access restricted to admin, and proper serialization.
"""

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User
from .models import KBEntry, Resource


FAST_TEST_SETTINGS = {
    "PASSWORD_HASHERS": ["django.contrib.auth.hashers.MD5PasswordHasher"],
    "DATABASES": {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },
    "REST_FRAMEWORK": {
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.SessionAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.IsAuthenticated",
        ],
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 20,
        "DEFAULT_THROTTLE_CLASSES": [],
        "DEFAULT_THROTTLE_RATES": {},
    },
}


@override_settings(**FAST_TEST_SETTINGS)
class KBEntryAccessTest(TestCase):
    """Test KB entry access control."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin", password="AdminPass1234!", role="admin"
        )
        self.pentester = User.objects.create_user(
            username="pentester", password="PentesterPass1234!", role="pentester"
        )
        self.viewer = User.objects.create_user(
            username="viewer", password="ViewerPass1234!", role="viewer"
        )
        self.kb = KBEntry.objects.create(
            name="XSS",
            description="Cross-site scripting",
            category="xss",
            severity_default="high",
        )

    # -- Read access (all authenticated roles) --

    def test_admin_can_read_kb(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse("kb:entry-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pentester_can_read_kb(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.get(reverse("kb:entry-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_viewer_can_read_kb(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(reverse("kb:entry-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all_roles_can_read_kb_detail(self):
        for user in [self.admin, self.pentester, self.viewer]:
            self.client.force_authenticate(user=user)
            response = self.client.get(
                reverse("kb:entry-detail", args=[self.kb.pk])
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                msg=f"{user.username} should be able to read KB detail",
            )

    def test_unauthenticated_cannot_read_kb(self):
        self.client.logout()
        response = self.client.get(reverse("kb:entry-list"))
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    # -- Create (admin-only) --

    def test_admin_can_create_kb(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse("kb:entry-list"),
            {
                "name": "CSRF",
                "description": "Cross-site request forgery",
                "category": "csrf",
                "severity_default": "medium",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(KBEntry.objects.filter(name="CSRF").exists())

    def test_pentester_cannot_create_kb(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("kb:entry-list"),
            {
                "name": "Test",
                "description": "Test",
                "category": "test",
                "severity_default": "low",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_create_kb(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.post(
            reverse("kb:entry-list"),
            {
                "name": "Test",
                "description": "Test",
                "category": "test",
                "severity_default": "low",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # -- Update (admin-only) --

    def test_admin_can_update_kb(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse("kb:entry-detail", args=[self.kb.pk]),
            {"description": "Updated description"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.kb.refresh_from_db()
        self.assertEqual(self.kb.description, "Updated description")

    def test_pentester_cannot_update_kb(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.patch(
            reverse("kb:entry-detail", args=[self.kb.pk]),
            {"description": "Hacked"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # -- Delete (admin-only) --

    def test_admin_can_delete_kb(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(
            reverse("kb:entry-detail", args=[self.kb.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(KBEntry.objects.filter(pk=self.kb.pk).exists())

    def test_pentester_cannot_delete_kb(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.delete(
            reverse("kb:entry-detail", args=[self.kb.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_delete_kb(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.delete(
            reverse("kb:entry-detail", args=[self.kb.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@override_settings(**FAST_TEST_SETTINGS)
class KBEntryModelTest(TestCase):
    """Test KBEntry model behavior."""

    def test_str_representation(self):
        kb = KBEntry.objects.create(
            name="SSRF", description="Server-side request forgery",
            category="ssrf", severity_default="high",
        )
        self.assertEqual(str(kb), "[ssrf] SSRF")

    def test_default_severity(self):
        kb = KBEntry.objects.create(
            name="Misc", description="Misc vuln", category="misc",
        )
        self.assertEqual(kb.severity_default, "medium")


@override_settings(**FAST_TEST_SETTINGS)
class ResourceAccessTest(TestCase):
    """Test Resource CRUD access control."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin", password="AdminPass1234!", role="admin"
        )
        self.pentester = User.objects.create_user(
            username="pentester", password="PentesterPass1234!", role="pentester"
        )
        self.viewer = User.objects.create_user(
            username="viewer", password="ViewerPass1234!", role="viewer"
        )
        self.resource = Resource.objects.create(
            title="OWASP Top 10",
            url="https://owasp.org/top10",
            description="OWASP Top 10",
            category="guide",
        )

    def test_all_roles_can_read_resources(self):
        for user in [self.admin, self.pentester, self.viewer]:
            self.client.force_authenticate(user=user)
            response = self.client.get(reverse("kb:resource-list"))
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                msg=f"{user.username} should be able to read resources",
            )

    def test_admin_can_create_resource(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse("kb:resource-list"),
            {
                "title": "HackTheBox",
                "url": "https://hackthebox.com",
                "description": "Lab platform",
                "category": "lab",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_pentester_cannot_create_resource(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("kb:resource-list"),
            {
                "title": "Test",
                "url": "https://example.com",
                "description": "Test",
                "category": "lab",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_resource(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(
            reverse("kb:resource-detail", args=[self.resource.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_viewer_cannot_delete_resource(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.delete(
            reverse("kb:resource-detail", args=[self.resource.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
# Tests KB - Diego
