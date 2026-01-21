from fastapi import APIRouter, HTTPException

from ..auth import CurrentUser, AuthUser
from ..clients import supabase_admin
from ..schemas import SignedUploadRequest, SignedUploadResponse

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/signed-upload", response_model=SignedUploadResponse)
async def signed_upload(body: SignedUploadRequest, user: AuthUser = CurrentUser) -> SignedUploadResponse:
    # Basic safety: prevent writing outside user's namespace unless you want shared buckets later.
    if not body.path.startswith(f"{user.id}/"):
        raise HTTPException(status_code=400, detail="path must start with '<userId>/'")

    sb = supabase_admin()
    try:
        res = sb.storage.from_(body.bucket).create_signed_upload_url(body.path)
        # supabase-py returns dict-like with fields: signedUrl, token, path (varies by version)
        signed_url = res.get("signedUrl") or res.get("signed_url")
        token = res.get("token")
        path = res.get("path") or body.path
        if not signed_url:
            raise RuntimeError("Missing signedUrl")
        return SignedUploadResponse(bucket=body.bucket, path=path, signed_url=signed_url, token=token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not create signed upload URL: {e}")

