import os
import secrets
import logging
import base64
import json
from urllib.parse import urlencode, urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.auth import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()
logger = logging.getLogger("uvicorn.error")

DEFAULT_FRONTEND_URL = "http://127.0.0.1:5173"
ALLOWED_FRONTEND_ORIGINS = {
    "http://127.0.0.1:5173",
    "http://localhost:5173",
}


def get_frontend_url() -> str:
    return os.getenv("FRONTEND_URL", DEFAULT_FRONTEND_URL).rstrip("/")


def get_frontend_url_from_request(request: Request) -> str:
    referer = request.headers.get("referer")
    if referer:
        parsed = urlparse(referer)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin in ALLOWED_FRONTEND_ORIGINS:
            return origin

    return get_frontend_url()


def encode_oauth_state(frontend_url: str) -> str:
    payload = json.dumps({"frontend_url": frontend_url}, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("ascii")


def decode_oauth_state(state: str | None) -> str:
    if not state:
        return get_frontend_url()

    try:
        payload = base64.urlsafe_b64decode(state.encode("ascii"))
        data = json.loads(payload.decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        return get_frontend_url()

    frontend_url = str(data.get("frontend_url", "")).rstrip("/")
    if frontend_url in ALLOWED_FRONTEND_ORIGINS:
        return frontend_url

    return get_frontend_url()


def redirect_to_oauth_callback(frontend_url: str, **params):
    return RedirectResponse(f"{frontend_url}/oauth/callback?{urlencode(params)}", status_code=302)


def get_google_credentials():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_OAUTH_REDIRECT", "http://127.0.0.1:8000/auth/google/callback")
    masked_client_id = f"{client_id[:12]}..." if client_id else None
    logger.info(
        "Google OAuth config - client_id: %s, client_secret exists: %s, redirect_uri: %s",
        masked_client_id,
        bool(client_secret),
        redirect_uri,
    )
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth no estÃ¡ configurado")
    return client_id, client_secret, redirect_uri


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"user_id": user.id, "role": user.role})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/google")
def google_login(request: Request):
    client_id, _, redirect_uri = get_google_credentials()
    frontend_url = get_frontend_url_from_request(request)
    logger.info("OAuth step 1: redirecting browser to Google with redirect_uri=%s", redirect_uri)
    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": redirect_uri,
        "access_type": "offline",
        "prompt": "select_account",
        "state": encode_oauth_state(frontend_url),
    }
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return RedirectResponse(google_auth_url, status_code=302)


@router.get("/google/callback")
async def google_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    frontend_url = decode_oauth_state(state)
    logger.info("OAuth step 2: backend callback reached. code present: %s", bool(code))
    if error:
        logger.error("OAuth error returned by Google: %s", error)
        return redirect_to_oauth_callback(frontend_url, error=error)

    if not code:
        return redirect_to_oauth_callback(frontend_url, error="missing_google_code")

    client_id, client_secret, redirect_uri = get_google_credentials()
    token_url = "https://oauth2.googleapis.com/token"
    logger.info("OAuth step 3: exchanging Google code for access token")

    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                token_url,
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=15.0,
            )
    except httpx.HTTPError as exc:
        logger.exception("OAuth error: Google token request failed: %s", exc)
        return redirect_to_oauth_callback(frontend_url, error="google_token_request_failed")

    logger.info("OAuth step 3 result: Google token endpoint status=%s", token_response.status_code)

    if token_response.status_code != 200:
        logger.error("OAuth error: Google token response=%s", token_response.text[:500])
        return redirect_to_oauth_callback(frontend_url, error="google_token_exchange_failed")

    token_data = token_response.json()
    access_token = token_data.get("access_token")
    logger.info("OAuth step 4: Google access_token present: %s", bool(access_token))
    if not access_token:
        return redirect_to_oauth_callback(frontend_url, error="missing_google_access_token")

    logger.info("OAuth step 5: requesting Google user profile")
    try:
        async with httpx.AsyncClient() as client:
            user_info_response = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=15.0,
            )
    except httpx.HTTPError as exc:
        logger.exception("OAuth error: Google userinfo request failed: %s", exc)
        return redirect_to_oauth_callback(frontend_url, error="google_userinfo_request_failed")

    logger.info("OAuth step 5 result: Google userinfo status=%s", user_info_response.status_code)

    if user_info_response.status_code != 200:
        logger.error("OAuth error: Google userinfo response=%s", user_info_response.text[:500])
        return redirect_to_oauth_callback(frontend_url, error="google_userinfo_failed")

    profile = user_info_response.json()
    email = profile.get("email")
    name = profile.get("name", "Usuario Google")
    logger.info("OAuth step 6: Google profile email present: %s", bool(email))

    if not email:
        return redirect_to_oauth_callback(frontend_url, error="missing_google_email")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.info("OAuth step 7: creating local user for Google email=%s", email)
        random_password = secrets.token_urlsafe(32)
        user = User(
            name=name,
            email=email,
            password=hash_password(random_password),
            role="user"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        logger.info("OAuth step 7: existing local user found. user_id=%s", user.id)

    token = create_access_token({"user_id": user.id, "role": user.role})
    redirect_url = f"{frontend_url}/oauth/callback?" + urlencode({"token": token})
    logger.info(
        "OAuth step 8: internal JWT created for user_id=%s. Redirecting to %s/oauth/callback?token=<hidden>",
        user.id,
        frontend_url,
    )
    return RedirectResponse(redirect_url, status_code=302)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return payload  # puedes devolver user_id si quieres

    except JWTError:
        raise HTTPException(status_code=401, detail="Token invÃ¡lido")
