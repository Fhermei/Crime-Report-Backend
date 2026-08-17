from rest_framework import serializers
from .models import CrimeReport, Evidence, StatusUpdate, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = ["id", "file_url", "file_type", "uploaded_at"]

class StatusUpdateSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source="updated_by.username", read_only=True, default=None)

    class Meta:
        model = StatusUpdate
        fields = ["id", "old_status", "new_status", "note", "timestamp", "updated_by_name"]

class CrimeReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrimeReport
        fields = [
            "id", "is_anonymous", "tracking_code", "crime_type", "description",
            "latitude", "longitude", "address", "incident_date", "urgency",
        ]
        read_only_fields = ["id", "tracking_code"]

    def validate(self, attrs):
        if not (-90 <= attrs["latitude"] <= 90) or not (-180 <= attrs["longitude"] <= 180):
            raise serializers.ValidationError("Invalid map coordinates. Please pin a valid location.")
        return attrs

class CrimeReportListSerializer(serializers.ModelSerializer):
    reporter_name = serializers.SerializerMethodField()
    evidence = EvidenceSerializer(many=True, read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    assigned_by_name = serializers.SerializerMethodField()

    class Meta:
        model = CrimeReport
        fields = [
            "id", "tracking_code", "is_anonymous", "reporter_name", "crime_type", "description",
            "latitude", "longitude", "address", "incident_date", "urgency", "status",
            "created_at", "updated_at", "evidence", "assigned_to", "assigned_to_name",
            "assigned_by", "assigned_by_name", "assigned_at"
        ]

    def get_reporter_name(self, obj):
        if obj.is_anonymous or obj.reporter is None:
            return "Anonymous"
        return obj.reporter.username

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip() or obj.assigned_to.username
        return None

    def get_assigned_by_name(self, obj):
        if obj.assigned_by:
            return f"{obj.assigned_by.first_name} {obj.assigned_by.last_name}".strip() or obj.assigned_by.username
        return None

class CrimeReportAdminSerializer(CrimeReportListSerializer):
    updates = StatusUpdateSerializer(many=True, read_only=True)

    class Meta(CrimeReportListSerializer.Meta):
        fields = CrimeReportListSerializer.Meta.fields + ["ip_address", "updates"]

class StatusChangeSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=CrimeReport.STATUS_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True)

class TrackReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrimeReport
        fields = ["tracking_code", "crime_type", "status", "urgency", "created_at", "updated_at"]

class AssignReportSerializer(serializers.Serializer):
    assigned_to = serializers.IntegerField()
    note = serializers.CharField(required=False, allow_blank=True)