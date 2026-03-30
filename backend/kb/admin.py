from django.contrib import admin

from .models import KBEntry, Resource


@admin.register(KBEntry)
class KBEntryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "severity_default", "updated_at")
    list_filter = ("category", "severity_default")
    search_fields = ("name", "description")
    ordering = ("category", "name")


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "url")
    list_filter = ("category",)
    search_fields = ("title", "description")
    ordering = ("category", "title")
