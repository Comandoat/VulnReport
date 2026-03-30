from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "actor", "action", "object_type", "object_id")
    list_filter = ("action", "object_type", "timestamp")
    search_fields = ("actor__username", "action", "object_type", "object_id")
    readonly_fields = (
        "actor",
        "action",
        "object_type",
        "object_id",
        "timestamp",
        "metadata",
    )
    ordering = ("-timestamp",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
