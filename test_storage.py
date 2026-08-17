"""
Test script to verify Supabase S3 storage is working.
Run: python test_storage.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

print("=" * 60)
print("TESTING FILE STORAGE")
print("=" * 60)

print(f"\n📁 Storage Backend: {default_storage.__class__.__name__}")
print(f"📁 Media URL: {settings.MEDIA_URL}")

# Check if using Supabase
if hasattr(settings, 'USE_SUPABASE_STORAGE') and settings.USE_SUPABASE_STORAGE:
    print("✅ Using Supabase S3 Storage")
    print(f"   Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"   Endpoint: {settings.AWS_S3_ENDPOINT_URL}")
else:
    print("⚠️ Using Local Storage")

# Test file upload
try:
    print("\n📤 Uploading test file...")
    test_content = ContentFile(b"This is a test file for storage.")
    test_path = default_storage.save("test/hello.txt", test_content)
    test_url = default_storage.url(test_path)
    print(f"✅ Upload successful!")
    print(f"   Path: {test_path}")
    print(f"   URL: {test_url}")
    
    # Clean up
    default_storage.delete(test_path)
    print("\n✅ Test file deleted")
    
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 60)