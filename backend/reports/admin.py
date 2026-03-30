from django.contrib import admin

from .models import Finding, Report


class FindingInline(admin.TabularInline):
    model = Finding
    extra = 0
    fields = ["title", "severity", "cvss_score", "order", "kb_entry"]
    readonly_fields = ["created_at"]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "owner", "created_at", "updated_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["title", "owner__username"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [FindingInline]


@admin.register(Finding)
class FindingAdmin(admin.ModelAdmin):
    list_display = ["title", "severity", "cvss_score", "report", "order", "created_at"]
    list_filter = ["severity", "report"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at"]
