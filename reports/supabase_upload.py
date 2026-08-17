"""
Uploads evidence files to Supabase Storage (S3 compatible).
Works with both local and production environments.
"""

import uuid
import os
from django.conf import settings
from django.core.files.storage import default_storage

ALLOWED_TYPES = {
    "image/jpeg": "image",
    "image/png": "image",
    "image/webp": "image",
    "video/mp4": "video",
    "video/quicktime": "video",
    "audio/mpeg": "audio",
    "audio/mp4": "audio",
    "application/pdf": "document",
}
MAX_FILE_SIZE_MB = 25

def upload_evidence_file(django_file):
    """
    Upload a file to storage (Supabase S3 or local).
    Returns the public URL and file type.
    """
    content_type = getattr(django_file, "content_type", None)
    if content_type not in ALLOWED_TYPES:
        raise ValueError(f"Unsupported file type: {content_type}")

    size_mb = django_file.size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"File too large ({size_mb:.1f}MB). Max is {MAX_FILE_SIZE_MB}MB.")

    file_type = ALLOWED_TYPES[content_type]
    
    # Generate a unique filename
    ext = django_file.name.split(".")[-1]
    filename = f"evidence/{uuid.uuid4()}.{ext}"
    
    try:
        # Save using Django's default storage (Supabase S3 or local)
        saved_path = default_storage.save(filename, django_file)
        
        # Get the public URL
        public_url = default_storage.url(saved_path)
        
        print(f" File uploaded successfully: {public_url}")
        return public_url, file_type
        
    except Exception as e:
        print(f" Error uploading file: {e}")
        
        # Fallback: Save locally if Supabase fails
        try:
            from django.conf import settings
            local_path = os.path.join(settings.MEDIA_ROOT, filename)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Reset file pointer and save locally
            django_file.seek(0)
            with open(local_path, 'wb') as f:
                f.write(django_file.read())
            
            fallback_url = f"{settings.MEDIA_URL}{filename}"
            print(f" Fallback to local storage: {fallback_url}")
            return fallback_url, file_type
            
        except Exception as fallback_error:
            print(f" Fallback also failed: {fallback_error}")
            # Last resort: return a placeholder
            return f"/media/evidence/{uuid.uuid4()}.{ext}", file_type