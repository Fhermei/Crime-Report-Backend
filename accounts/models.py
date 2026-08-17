from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ("citizen", "Citizen"),
        ("police", "Police"),
        ("admin", "Admin"),
    ]
    
    # Remove username requirement and make email the primary field
    email = models.EmailField(unique=True, error_messages={
        'unique': "A user with that email already exists.",
    })
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True, error_messages={
        'unique': "A user with that phone number already exists.",
    })
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="citizen")
    badge_number = models.CharField(max_length=30, blank=True, null=True, help_text="Police officers only")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Override the username field to not be required
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.email} ({self.role})"

    def save(self, *args, **kwargs):
        # If username is empty, generate from email
        if not self.username and self.email:
            base_username = self.email.split("@")[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            self.username = username
        super().save(*args, **kwargs)