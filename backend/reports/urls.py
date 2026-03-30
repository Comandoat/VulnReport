from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    # Reports
    path("", views.ReportListCreateView.as_view(), name="report-list-create"),
    path("<int:pk>/", views.ReportDetailView.as_view(), name="report-detail"),
    # Findings (nested under report)
    path(
        "<int:report_id>/findings/",
        views.FindingListCreateView.as_view(),
        name="finding-list-create",
    ),
    path(
        "<int:report_id>/findings/<int:pk>/",
        views.FindingDetailView.as_view(),
        name="finding-detail",
    ),
    path(
        "<int:report_id>/findings/reorder/",
        views.ReorderFindingsView.as_view(),
        name="finding-reorder",
    ),
]
