# students/supabase_storage.py
import os
import uuid
from django.conf import settings

# optional: supabase client import - imported lazily in _get_supabase_client()
from supabase import create_client
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def _get_supabase_client():
    """Lazy-create supabase client reading settings or env vars."""
    url = getattr(settings, "SUPABASE_URL", None) or os.environ.get("SUPABASE_URL")
    key = getattr(settings, "SUPABASE_KEY", None) or os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in settings or environment variables.")
    return create_client(url, key)


def upload_profile_picture(file_obj, bucket='public', user_path='profile_pics'):
    """
    Uploads a Django uploaded file (InMemoryUploadedFile) to Supabase Storage and returns a URL.
    If SUPABASE_* are not configured, it falls back to saving locally to MEDIA_ROOT.
    """
    # Defensive check: ensure file_obj looks like an uploaded file
    # Django uploaded files typically have .name and .read()
    if file_obj is None:
        raise ValueError("No file object provided to upload_profile_picture()")
    if not hasattr(file_obj, "name") or not hasattr(file_obj, "read"):
        raise TypeError("Expected a Django uploaded file (request.FILES['...']). Got: %s" % type(file_obj))

    # Read bytes (do this only once)
    data = file_obj.read()

    # Try Supabase upload first
    try:
        supabase = _get_supabase_client()
        ext = file_obj.name.split('.')[-1] if '.' in file_obj.name else ''
        filename = f"{user_path}/{uuid.uuid4().hex}{('.' + ext) if ext else ''}"

        res = supabase.storage.from_(bucket).upload(filename, data)
        # check for error shape
        if isinstance(res, dict) and res.get('error'):
            raise RuntimeError(f"Supabase upload error: {res['error']}")

        public = supabase.storage.from_(bucket).get_public_url(filename)
        if isinstance(public, dict):
            return public.get('publicURL') or public.get('public_url') or public.get('signedURL')
        return public
    except RuntimeError:
        # re-raise runtime errors (e.g., missing keys or supabase upload error)
        raise
    except Exception:
        # Fallback: save locally to MEDIA_ROOT (useful for dev)
        filename = f"{user_path}/{uuid.uuid4().hex}_{file_obj.name}"
        path = default_storage.save(filename, ContentFile(data))
        if settings.DEBUG:
            return settings.MEDIA_URL + path
        return default_storage.url(path)
