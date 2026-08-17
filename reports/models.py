import random
import string
import uuid
from django.conf import settings
from django.db import models

def generate_tracking_code():
    chars = string.ascii_uppercase + string.digits
    return "CR-" + "".join(random.choices(chars, k=6))

class CrimeReport(models.Model):
    CRIME_TYPE_CHOICES = [
        ("theft", "Theft"),
        ("assault", "Assault"),
        ("burglary", "Burglary"),
        ("fraud", "Fraud"),
        ("vandalism", "Vandalism"),
        ("harassment", "Harassment"),
        ("kidnapping", "Kidnapping"),
        ("domestic_violence", "Domestic Violence"),
        ("cybercrime", "Cybercrime"),
        ("other", "Other"),
    ]
    URGENCY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("emergency", "Emergency"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("investigating", "Investigating"),
        ("resolved", "Resolved"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="reports"
    )
    is_anonymous = models.BooleanField(default=False)
    tracking_code = models.CharField(max_length=12, unique=True, editable=False)

    crime_type = models.CharField(max_length=30, choices=CRIME_TYPE_CHOICES)
    description = models.TextField()

    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=255, blank=True)

    incident_date = models.DateTimeField()
    urgency = models.CharField(max_length=15, choices=URGENCY_CHOICES, default="low")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pending")

    # Assignment fields
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name="assigned_reports",
        limit_choices_to={'role': 'police'}
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_by_reports"
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            code = generate_tracking_code()
            while CrimeReport.objects.filter(tracking_code=code).exists():
                code = generate_tracking_code()
            self.tracking_code = code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tracking_code} - {self.crime_type} ({self.status})"

class Evidence(models.Model):
    FILE_TYPE_CHOICES = [("image", "Image"), ("video", "Video"), ("audio", "Audio"), ("document", "Document")]
    
    report = models.ForeignKey(CrimeReport, related_name="evidence", on_delete=models.CASCADE)
    file_url = models.URLField()
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidence for {self.report.tracking_code}"

class StatusUpdate(models.Model):
    report = models.ForeignKey(CrimeReport, related_name="updates", on_delete=models.CASCADE)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.report.tracking_code}: {self.old_status} -> {self.new_status}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    report = models.ForeignKey(CrimeReport, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]