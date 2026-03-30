from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdmin
from audit.utils import log_action

from .models import KBEntry, Resource
from .serializers import KBEntryListSerializer, KBEntrySerializer, ResourceSerializer


# ---------------------------------------------------------------------------
# KB Entries
# ---------------------------------------------------------------------------


class KBEntryListView(ListCreateAPIView):
    """
    GET  /api/kb/entries/      – all authenticated users (list)
    POST /api/kb/entries/      – admin only (create)
    """

    queryset = KBEntry.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category"]
    search_fields = ["name", "description"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return KBEntryListSerializer
        return KBEntrySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(
            actor=self.request.user,
            action="create_kb_entry",
            object_type="kb_entry",
            object_id=instance.pk,
            metadata={"name": instance.name, "category": instance.category},
        )


class KBEntryDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET    /api/kb/entries/<pk>/  – all authenticated users
    PATCH  /api/kb/entries/<pk>/  – admin only
    DELETE /api/kb/entries/<pk>/  – admin only
    """

    queryset = KBEntry.objects.all()
    serializer_class = KBEntrySerializer

    def get_permissions(self):
        if self.request.method in ("PATCH", "PUT", "DELETE"):
            return [IsAdmin()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(
            actor=self.request.user,
            action="update_kb_entry",
            object_type="kb_entry",
            object_id=instance.pk,
            metadata={"name": instance.name},
        )

    def perform_destroy(self, instance):
        entry_id = instance.pk
        entry_name = instance.name
        instance.delete()
        log_action(
            actor=self.request.user,
            action="delete_kb_entry",
            object_type="kb_entry",
            object_id=entry_id,
            metadata={"name": entry_name},
        )


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


class ResourceListView(ListCreateAPIView):
    """
    GET  /api/kb/resources/   – all authenticated users
    POST /api/kb/resources/   – admin only
    """

    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category"]
    search_fields = ["title", "description"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [IsAuthenticated()]


class ResourceDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET    /api/kb/resources/<pk>/  – all authenticated users
    PATCH  /api/kb/resources/<pk>/  – admin only
    DELETE /api/kb/resources/<pk>/  – admin only
    """

    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    def get_permissions(self):
        if self.request.method in ("PATCH", "PUT", "DELETE"):
            return [IsAdmin()]
        return [IsAuthenticated()]
