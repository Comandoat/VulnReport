from django.urls import path

from . import views

app_name = "kb"

urlpatterns = [
    path("entries/", views.KBEntryListView.as_view(), name="entry-list"),
    path("entries/<int:pk>/", views.KBEntryDetailView.as_view(), name="entry-detail"),
    path("resources/", views.ResourceListView.as_view(), name="resource-list"),
    path("resources/<int:pk>/", views.ResourceDetailView.as_view(), name="resource-detail"),
]
