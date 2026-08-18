"""
Complete test data loader for Crime Reporting System
Run: python test.py
"""

import os
import sys
import django
import random
from datetime import timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from reports.models import CrimeReport, Evidence, StatusUpdate, Notification

User = get_user_model()

# ============================================================
# SAMPLE DATA
# ============================================================

CRIME_TYPES = [
    "theft", "assault", "burglary", "fraud", "vandalism", 
    "harassment", "kidnapping", "domestic_violence", "cybercrime", "other"
]

URGENCY_LEVELS = ["low", "medium", "high", "emergency"]

DESCRIPTIONS = [
    "A man was seen breaking into a car at the parking lot. He took a laptop bag and ran away.",
    "Two individuals got into a physical fight at the market square. One was injured.",
    "Someone broke into the store last night and stole cash and electronics.",
    "Received a call from someone claiming to be from the bank asking for my PIN.",
    "The window of the house was smashed and items were stolen.",
    "Received threatening messages from an unknown number on social media.",
    "A child was reported missing from the school premises.",
    "A woman reported being physically assaulted by her partner.",
    "Someone hacked into my email and sent fraudulent messages to my contacts.",
    "A car was set on fire in the middle of the night.",
    "Suspicious person loitering around the neighborhood for several days.",
    "Package was stolen from the front porch.",
    "Identity theft - someone opened a bank account using my details.",
    "Vandalism - graffiti painted on the church wall.",
    "Hit and run accident at the intersection.",
]

LOCATIONS = [
    {"lat": 6.5244, "lng": 3.3792, "address": "Lagos Island, Lagos"},
    {"lat": 6.4550, "lng": 3.3941, "address": "Surulere, Lagos"},
    {"lat": 6.4654, "lng": 3.4064, "address": "Yaba, Lagos"},
    {"lat": 6.6019, "lng": 3.3515, "address": "Ikeja, Lagos"},
    {"lat": 6.5282, "lng": 3.3560, "address": "Victoria Island, Lagos"},
    {"lat": 6.4698, "lng": 3.3852, "address": "Mushin, Lagos"},
    {"lat": 6.6121, "lng": 3.0516, "address": "Ota, Ogun State"},
    {"lat": 6.4960, "lng": 3.3782, "address": "Lekki, Lagos"},
    {"lat": 6.5511, "lng": 3.3950, "address": "Apapa, Lagos"},
    {"lat": 6.5773, "lng": 3.2688, "address": "Agege, Lagos"},
]

# ============================================================
# MAIN FUNCTION
# ============================================================

def main():
    print("\n" + "=" * 60)
    print("🚀 LOADING TEST DATA")
    print("=" * 60)

    # ============================================================
    # CREATE USERS (11 Users: 1 Admin + 3 Police + 7 Citizens)
    # ============================================================

    print("\n📝 CREATING USERS")
    print("-" * 40)

    # Admin
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@crimesystem.com',
            'phone_number': '08012345678',
            'role': 'admin',
            'first_name': 'System',
            'last_name': 'Admin',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin.set_password('Admin@123')
        admin.save()
        print("  ✅ Created admin: admin@crimesystem.com / Admin@123")
    else:
        admin.set_password('Admin@123')
        admin.save()
        print("  ℹ️ Admin already exists - password reset")

    # Police officers (3)
    police_data = [
        {"username": "police_john", "email": "john.smith@police.com", "phone": "08023456789", 
         "first": "John", "last": "Smith", "badge": "P1001"},
        {"username": "police_mary", "email": "mary.johnson@police.com", "phone": "08034567890", 
         "first": "Mary", "last": "Johnson", "badge": "P1002"},
        {"username": "police_peter", "email": "peter.williams@police.com", "phone": "08045678901", 
         "first": "Peter", "last": "Williams", "badge": "P1003"},
    ]

    police_users = []
    for data in police_data:
        user, created = User.objects.get_or_create(
            username=data["username"],
            defaults={
                'email': data["email"],
                'phone_number': data["phone"],
                'role': 'police',
                'first_name': data["first"],
                'last_name': data["last"],
                'badge_number': data["badge"],
                'is_staff': True,
            }
        )
        if created:
            user.set_password('Police@123')
            user.save()
            print(f"  ✅ Created police: {data['email']} / Police@123")
        else:
            user.set_password('Police@123')
            user.save()
            print(f"  ℹ️ Police {data['first']} already exists")
        police_users.append(user)

    # Citizens (7)
    citizen_data = [
        {"username": "citizen_alice", "email": "alice.wonder@email.com", "phone": "08078901234", 
         "first": "Alice", "last": "Wonder"},
        {"username": "citizen_bob", "email": "bob.builder@email.com", "phone": "08089012345", 
         "first": "Bob", "last": "Builder"},
        {"username": "citizen_charlie", "email": "charlie.brown@email.com", "phone": "08090123456", 
         "first": "Charlie", "last": "Brown"},
        {"username": "citizen_david", "email": "david.smith@email.com", "phone": "08101234567", 
         "first": "David", "last": "Smith"},
        {"username": "citizen_emma", "email": "emma.watson@email.com", "phone": "08112345678", 
         "first": "Emma", "last": "Watson"},
        {"username": "citizen_frank", "email": "frank.ocean@email.com", "phone": "08123456789", 
         "first": "Frank", "last": "Ocean"},
        {"username": "citizen_grace", "email": "grace.hopper@email.com", "phone": "08134567890", 
         "first": "Grace", "last": "Hopper"},
    ]

    citizen_users = []
    for data in citizen_data:
        user, created = User.objects.get_or_create(
            username=data["username"],
            defaults={
                'email': data["email"],
                'phone_number': data["phone"],
                'role': 'citizen',
                'first_name': data["first"],
                'last_name': data["last"],
            }
        )
        if created:
            user.set_password('Citizen@123')
            user.save()
            print(f"  ✅ Created citizen: {data['email']} / Citizen@123")
        else:
            user.set_password('Citizen@123')
            user.save()
            print(f"  ℹ️ Citizen {data['first']} already exists")
        citizen_users.append(user)

    print(f"\n📊 Total users: {User.objects.count()}")

    # ============================================================
    # CREATE REPORTS (50 Reports)
    # ============================================================

    print("\n📝 CREATING 50 CRIME REPORTS")
    print("-" * 40)

    # Clear existing reports (optional - uncomment if you want fresh data)
    # CrimeReport.objects.all().delete()

    reports_created = []
    for i in range(50):
        is_anonymous = random.choice([True, False])
        reporter = None if is_anonymous else random.choice(citizen_users)
        
        location = random.choice(LOCATIONS)
        days_ago = random.randint(0, 30)
        incident_date = timezone.now() - timedelta(
            days=days_ago, 
            hours=random.randint(0, 23), 
            minutes=random.randint(0, 59)
        )
        
        # Weighted status: more pending (17), investigating (17), resolved (16)
        status_options = ["pending"] * 17 + ["investigating"] * 17 + ["resolved"] * 16
        status = random.choice(status_options)
        
        report = CrimeReport.objects.create(
            reporter=reporter,
            is_anonymous=is_anonymous,
            crime_type=random.choice(CRIME_TYPES),
            description=random.choice(DESCRIPTIONS),
            latitude=location["lat"] + random.uniform(-0.015, 0.015),
            longitude=location["lng"] + random.uniform(-0.015, 0.015),
            address=location["address"],
            incident_date=incident_date,
            urgency=random.choice(URGENCY_LEVELS),
            status=status,
            ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            created_at=incident_date,
            updated_at=incident_date + timedelta(hours=random.randint(1, 48)),
        )
        reports_created.append(report)

        # Add status updates for investigating/resolved
        if status in ["investigating", "resolved"]:
            # Pending -> Investigating
            StatusUpdate.objects.create(
                report=report,
                updated_by=random.choice(police_users),
                old_status="pending",
                new_status="investigating",
                note=f"Investigation started by {random.choice(police_users).first_name}.",
                timestamp=report.created_at + timedelta(hours=random.randint(1, 12)),
            )

        if status == "resolved":
            # Investigating -> Resolved
            StatusUpdate.objects.create(
                report=report,
                updated_by=random.choice(police_users),
                old_status="investigating",
                new_status="resolved",
                note=random.choice([
                    "Case resolved. Evidence found.",
                    "Suspect arrested and charged.",
                    "Matter settled amicably.",
                    "No further action needed.",
                    "Case closed successfully."
                ]),
                timestamp=report.created_at + timedelta(days=random.randint(1, 7), hours=random.randint(1, 23)),
            )

        # Add notifications for logged-in reporters
        if reporter and random.choice([True, False]):
            Notification.objects.create(
                user=reporter,
                report=report,
                message=f"Your report {report.tracking_code} has been updated to {status}.",
                is_read=random.choice([True, False]),
                created_at=report.created_at + timedelta(hours=random.randint(1, 24)),
            )

        if (i + 1) % 10 == 0:
            print(f"  ✅ Created {i + 1} reports...")

    print(f"\n📊 Total reports: {CrimeReport.objects.count()}")
    print(f"   Pending: {CrimeReport.objects.filter(status='pending').count()}")
    print(f"   Investigating: {CrimeReport.objects.filter(status='investigating').count()}")
    print(f"   Resolved: {CrimeReport.objects.filter(status='resolved').count()}")

    # ============================================================
    # CREATE EVIDENCE
    # ============================================================

    print("\n📝 CREATING EVIDENCE")
    print("-" * 40)

    evidence_urls = [
        "https://images.unsplash.com/photo-1582139329536-e7284fece509?w=300",
        "https://images.unsplash.com/photo-1577563908411-5077b6dc7624?w=300",
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=300",
        "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=300",
    ]

    evidence_types = ["image", "video", "audio", "document"]
    evidence_created = 0

    for report in random.sample(reports_created, min(30, len(reports_created))):
        num_evidence = random.randint(1, 3)
        for _ in range(num_evidence):
            Evidence.objects.create(
                report=report,
                file_url=random.choice(evidence_urls),
                file_type=random.choice(evidence_types),
                uploaded_at=report.created_at + timedelta(hours=random.randint(0, 2)),
            )
            evidence_created += 1

    print(f"  ✅ Created {evidence_created} evidence entries")

    # ============================================================
    # SUMMARY
    # ============================================================

    print("\n" + "=" * 60)
    print("✅ TEST DATA LOADING COMPLETE!")
    print("=" * 60)

    print("\n📊 DATABASE SUMMARY:")
    print(f"  👤 Users: {User.objects.count()}")
    print(f"     Admin: {User.objects.filter(role='admin').count()}")
    print(f"     Police: {User.objects.filter(role='police').count()}")
    print(f"     Citizens: {User.objects.filter(role='citizen').count()}")

    print(f"\n  📋 Crime Reports: {CrimeReport.objects.count()}")
    print(f"     Pending: {CrimeReport.objects.filter(status='pending').count()}")
    print(f"     Investigating: {CrimeReport.objects.filter(status='investigating').count()}")
    print(f"     Resolved: {CrimeReport.objects.filter(status='resolved').count()}")

    print(f"\n  📎 Status Updates: {StatusUpdate.objects.count()}")
    print(f"  🖼️ Evidence Files: {Evidence.objects.count()}")
    print(f"  🔔 Notifications: {Notification.objects.count()}")

    print("\n🔑 LOGIN CREDENTIALS:")
    print("  👑 Admin: admin@crimesystem.com / Admin@123")
    print("  👮 Police: john.smith@police.com / Police@123")
    print("  👤 Citizen: alice.wonder@email.com / Citizen@123")

    print("\n💡 TIP: Use email address to login, not username!")
    print("=" * 60)

if __name__ == "__main__":
    main()