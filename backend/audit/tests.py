"""
Comprehensive tests for the audit app.

Covers: AuditLog creation via log_action utility, immutability (no update,
no delete), and admin-only access to the audit log API.
"""

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User
from .models import AuditLog
from .utils import log_action


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
class AuditLogUtilTest(TestCase):
    """Test the log_action utility function."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="AdminPass1234!", role="admin"
        )

    def test_log_action_creates_entry(self):
        log_action(self.admin, "test_action", "test_object", "1", {"key": "value"})
        self.assertEqual(AuditLog.objects.count(), 1)
        entry = AuditLog.objects.first()
        self.assertEqual(entry.action, "test_action")
        self.assertEqual(entry.object_type, "test_object")
        self.assertEqual(entry.object_id, "1")
        self.assertEqual(entry.metadata, {"key": "value"})
        self.assertEqual(entry.actor, self.admin)

    def test_log_action_default_metadata(self):
        log_action(self.admin, "login", "user", "1")
        entry = AuditLog.objects.first()
        self.assertEqual(entry.metadata, {})

    def test_log_action_default_object_id(self):
        log_action(self.admin, "login", "user")
        entry = AuditLog.objects.first()
        self.assertEqual(entry.object_id, "")

    def test_multiple_log_entries(self):
        log_action(self.admin, "action1", "type1", "1")
        log_action(self.admin, "action2", "type2", "2")
        self.assertEqual(AuditLog.objects.count(), 2)


@override_settings(**FAST_TEST_SETTINGS)
class AuditLogImmutabilityTest(TestCase):
    """Test that audit log entries are immutable."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="AdminPass1234!", role="admin"
        )

    def test_audit_log_immutable_no_update(self):
        log = AuditLog.objects.create(
            actor=self.admin, action="test", object_type="test"
        )
        log.action = "modified"
        with self.assertRaises(ValueError):
            log.save()

    def test_audit_log_not_deletable(self):
        log = AuditLog.objects.create(
            actor=self.admin, action="test", object_type="test"
        )
        with self.assertRaises(ValueError):
            log.delete()

    def test_audit_log_str(self):
        log = AuditLog.objects.create(
            actor=self.admin, action="login", object_type="user"
        )
        self.assertIn("login", str(log))
        self.assertIn("admin", str(log))


@override_settings(**FAST_TEST_SETTINGS)
class AuditLogAPITest(TestCase):
    """Test the audit log list API endpoint."""

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
        # Create some log entries
        log_action(self.admin, "login", "user", str(self.admin.pk))
        log_action(self.pentester, "login", "user", str(self.pentester.pk))

    def test_admin_can_view_logs(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse("audit:log-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 2)

    def test_pentester_cannot_view_logs(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.get(reverse("audit:log-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_view_logs(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(reverse("audit:log-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_view_logs(self):
        response = self.client.get(reverse("audit:log-list"))
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_log_entries_are_read_only_via_api(self):
        """Verify the API does not expose POST/PUT/DELETE."""
        self.client.force_authenticate(user=self.admin)
        # POST should not be allowed (ListAPIView only supports GET)
        response = self.client.post(
            reverse("audit:log-list"),
            {"action": "fake", "object_type": "fake"},
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_audit_log_serialization(self):
        """Verify response contains expected fields."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse("audit:log-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        entry = response.data["results"][0]
        self.assertIn("id", entry)
        self.assertIn("actor", entry)
        self.assertIn("action", entry)
        self.assertIn("object_type", entry)
        self.assertIn("object_id", entry)
        self.assertIn("timestamp", entry)
        self.assertIn("metadata", entry)
        # Actor is serialized as nested object
        self.assertIn("id", entry["actor"])
        self.assertIn("username", entry["actor"])


@override_settings(**FAST_TEST_SETTINGS)
class AuditLogIntegrationTest(TestCase):
    """Test that actions in other apps create audit log entries."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin", password="AdminPass1234!", role="admin"
        )

    def test_login_creates_audit_entry(self):
        initial_count = AuditLog.objects.count()
        self.client.post(
            reverse("accounts:login"),
            {"username": "admin", "password": "AdminPass1234!"},
        )
        self.assertGreater(AuditLog.objects.count(), initial_count)
        log = AuditLog.objects.filter(action="login").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.actor, self.admin)

    def test_register_creates_audit_entry(self):
        self.client.force_authenticate(user=self.admin)
        self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "new@test.com",
                "password": "NewUserPass1234!",
                "role": "viewer",
            },
        )
        log = AuditLog.objects.filter(action="register_user").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.metadata["username"], "newuser")
# Tests audit - Diego
