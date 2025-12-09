# debug/views.py  (temporary - remove after use)
from django.http import JsonResponse
from django.conf import settings

def debug_env(request):
    """
    Temporary endpoint: returns basic settings for debugging.
    IMPORTANT: Do not leave this deployed long-term.
    """
    db = settings.DATABASES.get('default', {})
    response = {
        # Database info (non-secret)
        "DB_ENGINE": db.get("ENGINE"),
        "DB_HOST": db.get("HOST"),
        "DB_PORT": db.get("PORT"),
        "DB_NAME": db.get("NAME"),

        # Confirm whether DATABASE_URL is in use
        "USING_DATABASE_URL": bool(db.get("NAME")),  # presence of name => DB configured

        # Supabase config presence (do not output full key)
        "HAS_SUPABASE_URL": bool(getattr(settings, "SUPABASE_URL", None)),
        "HAS_SUPABASE_KEY": bool(getattr(settings, "SUPABASE_KEY", None)),

        # Django debug mode
        "DEBUG": settings.DEBUG,
    }

    return JsonResponse(response)
