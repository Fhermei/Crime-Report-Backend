from django.contrib import admin
from .models import CrimeReport, Evidence, StatusUpdate, Notification

class EvidenceInline(admin.TabularInline):
    model = Evidence
    extra = 1
    readonly_fields = ("file_url", "file_type", "uploaded_at")
    fields = ("file_url", "file_type", "uploaded_at")

class StatusUpdateInline(admin.TabularInline):
    model = StatusUpdate
    extra = 0
    readonly_fields = ("old_status", "new_status", "updated_by", "note", "timestamp")
    fields = ("old_status", "new_status", "updated_by", "note", "timestamp")
    can_delete = False

@admin.register(CrimeReport)
class CrimeReportAdmin(admin.ModelAdmin):
    list_display = ("tracking_code", "crime_type", "urgency", "status", "is_anonymous", "created_at", "ip_address")
    list_filter = ("status", "urgency", "crime_type", "is_anonymous")
    search_fields = ("tracking_code", "description", "address", "crime_type")
    readonly_fields = ("tracking_code", "ip_address", "created_at", "updated_at")
    fieldsets = (
        ("Report Info", {
            "fields": ("tracking_code", "crime_type", "description", "incident_date", "urgency", "status")
        }),
        ("Location", {
            "fields": ("latitude", "longitude", "address")
        }),
        ("Reporter Info", {
            "fields": ("reporter", "is_anonymous", "ip_address")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    inlines = [EvidenceInline, StatusUpdateInline]
    actions = ["mark_as_resolved", "mark_as_investigating"]

    def mark_as_resolved(self, request, queryset):
        queryset.update(status="resolved")
    mark_as_resolved.short_description = "Mark selected reports as Resolved"

    def mark_as_investigating(self, request, queryset):
        queryset.update(status="investigating")
    mark_as_investigating.short_description = "Mark selected reports as Investigating"

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "report", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "message")
    readonly_fields = ("created_at",)