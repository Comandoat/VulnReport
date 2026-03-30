"""
Comprehensive tests for the accounts app.

Covers: User model, authentication (login/logout), registration,
RBAC (role-based access control), user management, and password changes.
"""

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .models import User


# ---------------------------------------------------------------------------
# Use a fast hasher and disable throttling for test speed
# ---------------------------------------------------------------------------
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
class UserModelTest(TestCase):
    """Test custom User model."""

    def test_create_user_with_role_pentester(self):
        user = User.objects.create_user(
            username="test", password="TestPass1234!", role="pentester"
        )
        self.assertEqual(user.role, "pentester")
        self.assertTrue(user.is_pentester)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_viewer)

    def test_create_user_with_role_admin(self):
        user = User.objects.create_user(
            username="admin", password="TestPass1234!", role="admin"
        )
        self.assertEqual(user.role, "admin")
        self.assertTrue(user.is_admin)
        self.assertFalse(user.is_pentester)
        self.assertFalse(user.is_viewer)

    def test_default_role_is_viewer(self):
        user = User.objects.create_user(username="test", password="TestPass1234!")
        self.assertEqual(user.role, "viewer")
        self.assertTrue(user.is_viewer)

    def test_user_str(self):
        user = User.objects.create_user(
            username="alice", password="TestPass1234!", role="pentester"
        )
        self.assertEqual(str(user), "alice (pentester)")

    def test_role_choices(self):
        choices = [c[0] for c in User.Role.choices]
        self.assertIn("viewer", choices)
        self.assertIn("pentester", choices)
        self.assertIn("admin", choices)


@override_settings(**FAST_TEST_SETTINGS)
class AuthenticationTest(TestCase):
    """Test login / logout / me endpoints."""

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

    def test_login_success(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "admin", "password": "AdminPass1234!"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["role"], "admin")
        self.assertIn("csrf_token", response.data)

    def test_login_wrong_password(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "admin", "password": "WrongPassword!"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "noone", "password": "Whatever1234!"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_disabled_account_returns_401(self):
        """Anti-enumeration: disabled account returns same error as wrong password."""
        self.admin.is_active = False
        self.admin.save()
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "admin", "password": "AdminPass1234!"},
        )
        # Django's authenticate() returns None for inactive users by default,
        # so the view falls into the "user is None" branch => 401.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_unauthenticated(self):
        response = self.client.post(reverse("accounts:logout"))
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_me_endpoint(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.get(reverse("accounts:me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "pentester")
        self.assertEqual(response.data["role"], "pentester")

    def test_me_unauthenticated(self):
        response = self.client.get(reverse("accounts:me"))
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )


@override_settings(**FAST_TEST_SETTINGS)
class RBACTest(TestCase):
    """Test Role-Based Access Control across accounts endpoints."""

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

    # -- User list (admin-only) --

    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse("accounts:user-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pentester_cannot_list_users(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.get(reverse("accounts:user-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_list_users(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(reverse("accounts:user-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # -- Registration (admin-only) --

    def test_admin_can_register_user(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "new@test.com",
                "password": "NewUserPass1234!",
                "role": "pentester",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_pentester_cannot_register_user(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "new@test.com",
                "password": "NewUserPass1234!",
                "role": "viewer",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_register_user(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "new@test.com",
                "password": "NewUserPass1234!",
                "role": "viewer",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_register_duplicate_email_rejected(self):
        self.client.force_authenticate(user=self.admin)
        self.client.post(
            reverse("accounts:register"),
            {
                "username": "first",
                "email": "dup@test.com",
                "password": "FirstUserPass1234!",
                "role": "viewer",
            },
        )
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "second",
                "email": "dup@test.com",
                "password": "SecondUserPass1234!",
                "role": "viewer",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -- User detail (admin-only) --

    def test_admin_can_view_user_detail(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            reverse("accounts:user-detail", args=[self.pentester.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "pentester")

    def test_admin_can_update_user_role(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse("accounts:user-detail", args=[self.viewer.pk]),
            {"role": "pentester"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.viewer.refresh_from_db()
        self.assertEqual(self.viewer.role, "pentester")

    def test_admin_cannot_deactivate_self(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse("accounts:user-detail", args=[self.admin.pk]),
            {"is_active": False},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_cannot_change_own_role(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse("accounts:user-detail", args=[self.admin.pk]),
            {"role": "viewer"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_deactivate_other_user(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse("accounts:user-detail", args=[self.pentester.pk]),
            {"is_active": False},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pentester.refresh_from_db()
        self.assertFalse(self.pentester.is_active)

    def test_pentester_cannot_access_user_detail(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.get(
            reverse("accounts:user-detail", args=[self.admin.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # -- Password change --

    def test_password_change_success(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("accounts:change-password"),
            {
                "old_password": "PentesterPass1234!",
                "new_password": "NewPentester1234!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pentester.refresh_from_db()
        self.assertTrue(self.pentester.check_password("NewPentester1234!"))

    def test_password_change_wrong_old_password(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("accounts:change-password"),
            {
                "old_password": "WrongOldPassword!",
                "new_password": "NewPentester1234!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_password_rejected(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("accounts:change-password"),
            {
                "old_password": "PentesterPass1234!",
                "new_password": "12345678",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_password_rejected(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("accounts:change-password"),
            {
                "old_password": "PentesterPass1234!",
                "new_password": "Short1!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_cannot_change_password(self):
        response = self.client.post(
            reverse("accounts:change-password"),
            {
                "old_password": "PentesterPass1234!",
                "new_password": "NewPentester1234!",
            },
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )
# Tests accounts - Noa
