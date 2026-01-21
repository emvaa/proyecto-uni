from supabase import Client, create_client

from .settings import settings


def supabase_admin() -> Client:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError("Server misconfigured: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY missing")
    return create_client(settings.supabase_url, settings.supabase_service_role_key)

