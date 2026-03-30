"""
Comprehensive tests for the reports app.

Covers: report CRUD, ownership isolation, RBAC per role,
status transition validation, findings (CRUD, KB pre-fill, CVSS validation),
and finding reordering.
"""

from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User
from kb.models import KBEntry
from .models import Finding, Report


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
class ReportOwnershipTest(TestCase):
    """Test that pentesters can only manage their own reports."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin", password="AdminPass1234!", role="admin"
        )
        self.pentester1 = User.objects.create_user(
            username="pentester1", password="Pass1234Pass!", role="pentester"
        )
        self.pentester2 = User.objects.create_user(
            username="pentester2", password="Pass1234Pass!", role="pentester"
        )
        self.viewer = User.objects.create_user(
            username="viewer", password="ViewerPass1234!", role="viewer"
        )

        self.report1 = Report.objects.create(
            title="Report P1", owner=self.pentester1, status="draft"
        )
        self.report2 = Report.objects.create(
            title="Report P2", owner=self.pentester2, status="draft"
        )
        self.published_report = Report.objects.create(
            title="Published", owner=self.pentester1, status="published"
        )

    # -- List visibility --

    def test_pentester_sees_own_reports(self):
        self.client.force_authenticate(user=self.pentester1)
        response = self.client.get(reverse("reports:report-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [r["title"] for r in response.data["results"]]
        self.assertIn("Report P1", titles)
        self.assertIn("Published", titles)
        self.assertNotIn("Report P2", titles)

    def test_pentester_cannot_see_others_draft(self):
        self.client.force_authenticate(user=self.pentester1)
        response = self.client.get(reverse("reports:report-list-create"))
        titles = [r["title"] for r in response.data["results"]]
        self.assertNotIn("Report P2", titles)

    def test_admin_sees_all_reports(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse("reports:report-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 3)

    def test_viewer_sees_only_published(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(reverse("reports:report-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for r in response.data["results"]:
            self.assertEqual(r["status"], "published")

    # -- Edit / Delete ownership --

    def test_pentester_cannot_edit_others_report(self):
        self.client.force_authenticate(user=self.pentester1)
        response = self.client.patch(
            reverse("reports:report-detail", args=[self.report2.pk]),
            {"title": "Hacked"},
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND],
        )

    def test_pentester_cannot_delete_others_report(self):
        self.client.force_authenticate(user=self.pentester1)
        response = self.client.delete(
            reverse("reports:report-detail", args=[self.report2.pk])
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND],
        )

    def test_pentester_can_edit_own_report(self):
        self.client.force_authenticate(user=self.pentester1)
        response = self.client.patch(
            reverse("reports:report-detail", args=[self.report1.pk]),
            {"title": "Updated Title"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.report1.refresh_from_db()
        self.assertEqual(self.report1.title, "Updated Title")

    def test_pentester_can_delete_own_report(self):
        self.client.force_authenticate(user=self.pentester1)
        response = self.client.delete(
            reverse("reports:report-detail", args=[self.report1.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Report.objects.filter(pk=self.report1.pk).exists())

    def test_admin_can_delete_any_report(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(
            reverse("reports:report-detail", args=[self.report1.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_edit_any_report(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse("reports:report-detail", args=[self.report2.pk]),
            {"title": "Admin Edit"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -- Create --

    def test_viewer_cannot_create_report(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.post(
            reverse("reports:report-list-create"), {"title": "Viewer Report"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_report_auto_sets_owner(self):
        self.client.force_authenticate(user=self.pentester1)
        response = self.client.post(
            reverse("reports:report-list-create"), {"title": "New Report"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        report = Report.objects.get(pk=response.data["id"])
        self.assertEqual(report.owner, self.pentester1)
        self.assertEqual(report.status, "draft")

    def test_admin_can_create_report(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse("reports:report-list-create"), {"title": "Admin Report"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # -- Unauthenticated --

    def test_unauthenticated_cannot_access(self):
        response = self.client.get(reverse("reports:report-list-create"))
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )


@override_settings(**FAST_TEST_SETTINGS)
class ReportStatusTransitionTest(TestCase):
    """Test status transition validation: draft -> in_progress -> finalized -> published."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin", password="AdminPass1234!", role="admin"
        )
        self.pentester = User.objects.create_user(
            username="pentester", password="Pass1234Pass!", role="pentester"
        )
        self.report = Report.objects.create(
            title="Status Report", owner=self.pentester, status="draft"
        )

    def test_cannot_jump_draft_to_published(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse("reports:report-detail", args=[self.report.pk]),
            {"status": "published"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_jump_draft_to_finalized(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.patch(
            reverse("reports:report-detail", args=[self.report.pk]),
            {"status": "finalized"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_transition_draft_to_in_progress(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.patch(
            reverse("reports:report-detail", args=[self.report.pk]),
            {"status": "in_progress"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, "in_progress")

    def test_valid_full_lifecycle(self):
        """Test the full lifecycle: draft -> in_progress -> finalized -> published."""
        # draft -> in_progress (pentester)
        self.client.force_authenticate(user=self.pentester)
        resp = self.client.patch(
            reverse("reports:report-detail", args=[self.report.pk]),
            {"status": "in_progress"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # in_progress -> finalized (pentester)
        resp = self.client.patch(
            reverse("reports:report-detail", args=[self.report.pk]),
            {"status": "finalized"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # finalized -> published (admin only)
        self.client.force_authenticate(user=self.admin)
        resp = self.client.patch(
            reverse("reports:report-detail", args=[self.report.pk]),
            {"status": "published"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, "published")

    def test_pentester_cannot_publish(self):
        """Only admins can set status to published."""
        self.report.status = "finalized"
        self.report.save()
        self.client.force_authenticate(user=self.pentester)
        response = self.client.patch(
            reverse("reports:report-detail", args=[self.report.pk]),
            {"status": "published"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_go_backwards(self):
        self.report.status = "in_progress"
        self.report.save()
        self.client.force_authenticate(user=self.pentester)
        response = self.client.patch(
            reverse("reports:report-detail", args=[self.report.pk]),
            {"status": "draft"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@override_settings(**FAST_TEST_SETTINGS)
class FindingTest(TestCase):
    """Test findings CRUD, KB pre-fill, and CVSS validation."""

    def setUp(self):
        self.client = APIClient()
        self.pentester = User.objects.create_user(
            username="pentester", password="Pass1234Pass!", role="pentester"
        )
        self.other_pentester = User.objects.create_user(
            username="other", password="Pass1234Pass!", role="pentester"
        )
        self.report = Report.objects.create(
            title="Test Report", owner=self.pentester, status="draft"
        )
        self.other_report = Report.objects.create(
            title="Other Report", owner=self.other_pentester, status="draft"
        )
        self.kb_entry = KBEntry.objects.create(
            name="SQL Injection",
            description="SQLi desc",
            recommendation="Use ORM",
            references="CWE-89",
            severity_default="critical",
            category="injection",
        )

    def test_create_finding_from_kb(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("reports:finding-list-create", args=[self.report.pk]),
            {"title": "SQLi Finding", "kb_entry": self.kb_entry.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        finding = Finding.objects.get(pk=response.data["id"])
        self.assertEqual(finding.report, self.report)
        self.assertEqual(finding.kb_entry, self.kb_entry)

    def test_create_custom_finding(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("reports:finding-list-create", args=[self.report.pk]),
            {"title": "Custom Finding", "description": "Found XSS", "severity": "high"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["severity"], "high")

    def test_cvss_score_validation_too_high(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("reports:finding-list-create", args=[self.report.pk]),
            {"title": "Bad CVSS", "cvss_score": "11.0", "severity": "high"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cvss_score_validation_negative(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("reports:finding-list-create", args=[self.report.pk]),
            {"title": "Bad CVSS", "cvss_score": "-1.0", "severity": "high"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cvss_score_valid(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("reports:finding-list-create", args=[self.report.pk]),
            {"title": "Good CVSS", "cvss_score": "9.8", "severity": "critical"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        finding = Finding.objects.get(pk=response.data["id"])
        self.assertEqual(finding.cvss_score, Decimal("9.8"))

    def test_list_findings(self):
        Finding.objects.create(
            title="F1", severity="high", report=self.report
        )
        Finding.objects.create(
            title="F2", severity="low", report=self.report
        )
        self.client.force_authenticate(user=self.pentester)
        response = self.client.get(
            reverse("reports:finding-list-create", args=[self.report.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pentester_cannot_add_finding_to_others_report(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("reports:finding-list-create", args=[self.other_report.pk]),
            {"title": "Sneaky Finding", "severity": "high"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_finding(self):
        finding = Finding.objects.create(
            title="To Delete", severity="medium", report=self.report
        )
        self.client.force_authenticate(user=self.pentester)
        response = self.client.delete(
            reverse(
                "reports:finding-detail",
                args=[self.report.pk, finding.pk],
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Finding.objects.filter(pk=finding.pk).exists())

    def test_kb_prefill_populates_empty_fields(self):
        """When creating a finding from KB entry, empty fields are pre-filled."""
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("reports:finding-list-create", args=[self.report.pk]),
            {"title": "", "kb_entry": self.kb_entry.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        finding = Finding.objects.get(pk=response.data["id"])
        # The KB entry name is "SQL Injection" but the prefill maps 'title'
        # to kb_entry.title which doesn't exist; it maps name->name.
        # Based on the serializer, it checks hasattr(kb_entry, field).
        # KBEntry has 'description', 'recommendation', 'references' but
        # 'title' maps to 'name' via the prefill_fields list which includes 'title'
        # but KBEntry doesn't have a 'title' attr. So description should be filled.
        self.assertEqual(finding.description, "SQLi desc")
        self.assertEqual(finding.recommendation, "Use ORM")


@override_settings(**FAST_TEST_SETTINGS)
class FindingReorderTest(TestCase):
    """Test the findings reorder endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.pentester = User.objects.create_user(
            username="pentester", password="Pass1234Pass!", role="pentester"
        )
        self.report = Report.objects.create(
            title="Reorder Report", owner=self.pentester, status="draft"
        )
        self.f1 = Finding.objects.create(
            title="F1", severity="high", report=self.report, order=0
        )
        self.f2 = Finding.objects.create(
            title="F2", severity="medium", report=self.report, order=1
        )
        self.f3 = Finding.objects.create(
            title="F3", severity="low", report=self.report, order=2
        )

    def test_reorder_findings(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("reports:finding-reorder", args=[self.report.pk]),
            {"finding_ids": [self.f3.pk, self.f1.pk, self.f2.pk]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.f1.refresh_from_db()
        self.f2.refresh_from_db()
        self.f3.refresh_from_db()
        self.assertEqual(self.f3.order, 0)
        self.assertEqual(self.f1.order, 1)
        self.assertEqual(self.f2.order, 2)

    def test_reorder_incomplete_list_rejected(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("reports:finding-reorder", args=[self.report.pk]),
            {"finding_ids": [self.f1.pk]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reorder_invalid_ids_rejected(self):
        self.client.force_authenticate(user=self.pentester)
        response = self.client.post(
            reverse("reports:finding-reorder", args=[self.report.pk]),
            {"finding_ids": [self.f1.pk, self.f2.pk, 99999]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
# Tests reports - Noa
