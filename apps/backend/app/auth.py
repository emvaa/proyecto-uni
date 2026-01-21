from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx
from fastapi import Depends, HTTPException, Request
from jose import jwt

from .settings import settings


@dataclass
class AuthUser:
    id: str
    email: str | None
    raw: dict[str, Any]


_jwks_cache: dict[str, Any] | None = None
_jwks_cache_exp: float = 0.0


async def _get_jwks() -> dict[str, Any]:
    global _jwks_cache, _jwks_cache_exp
    if not settings.supabase_jwks_url:
        raise HTTPException(status_code=500, detail="Server misconfigured: SUPABASE_JWKS_URL is missing")
    now = time.time()
    if _jwks_cache is not None and now < _jwks_cache_exp:
        return _jwks_cache

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(settings.supabase_jwks_url)
        resp.raise_for_status()
        _jwks_cache = resp.json()
        _jwks_cache_exp = now + 60 * 10  # 10 min
        return _jwks_cache


async def get_current_user(request: Request) -> AuthUser:
    auth = request.headers.get("authorization") or ""
    if not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = auth.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="Invalid token header")

        jwks = await _get_jwks()
        keys = jwks.get("keys", [])
        key = next((k for k in keys if k.get("kid") == kid), None)
        if key is None:
            # Refresh once if key rotated
            global _jwks_cache_exp
            _jwks_cache_exp = 0
            jwks = await _get_jwks()
            keys = jwks.get("keys", [])
            key = next((k for k in keys if k.get("kid") == kid), None)
        if key is None:
            raise HTTPException(status_code=401, detail="Unknown signing key")

        # Supabase tokens are usually RS256
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return AuthUser(id=sub, email=payload.get("email"), raw=payload)


CurrentUser = Depends(get_current_user)

