import datetime
from urllib.parse import urlencode

import jwt
import requests
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.config import settings

router = APIRouter()

JWT_SECRET = settings.jwt_secret or "change-me-please"
JWT_ALGO = "HS256"
ACCESS_EXPIRE_SECONDS = settings.access_token_expire_minutes * 60

SUPABASE_URL = settings.supabase_url
SUPABASE_KEY = settings.supabase_key


def supabase_request(path: str, json_body: dict | None = None, method: str = "GET", token: str | None = None):
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Supabase credentials not configured")

    headers = {"apikey": SUPABASE_KEY}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if json_body is not None:
        headers["Content-Type"] = "application/json"

    response = requests.request(
        method=method,
        url=f"{SUPABASE_URL}/auth/v1/{path}",
        headers=headers,
        json=json_body,
        timeout=10,
    )

    if response.status_code >= 400:
        try:
            detail = response.json()
        except ValueError:
            detail = {"message": response.text}
        raise HTTPException(status_code=response.status_code, detail=detail)

    return response.json()


class SignupPayload(BaseModel):
    email: str
    password: str
    name: str | None = None


class LoginPayload(BaseModel):
    email: str
    password: str


def create_access_token(data: dict):
    if JWT_SECRET in {"", "change-me-please"}:
        raise HTTPException(status_code=500, detail="JWT_SECRET is not configured")
    to_encode = data.copy()
    now = datetime.datetime.utcnow()
    to_encode.update({"exp": now + datetime.timedelta(seconds=ACCESS_EXPIRE_SECONDS)})
    encoded = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO)
    return encoded


def decode_token(token: str):
    if not token:
        return None

    try:
        return supabase_request("user", token=token, method="GET")
    except HTTPException as exc:
        if exc.status_code in {401, 403}:
            try:
                return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
            except jwt.PyJWTError:
                return None
        raise


@router.post("/auth/signup")
def signup(payload: SignupPayload):
    data = supabase_request(
        "signup",
        json_body={
            "email": payload.email,
            "password": payload.password,
            "data": {"name": payload.name or payload.email.split("@", 1)[0]},
        },
        method="POST",
    )
    return {"access_token": data.get("access_token"), "token_type": "bearer", "user": data.get("user")}


@router.post("/auth/login")
def login(payload: LoginPayload):
    data = supabase_request(
        "token?grant_type=password",
        json_body={
            "email": payload.email,
            "password": payload.password,
        },
        method="POST",
    )
    return {"access_token": data.get("access_token"), "token_type": "bearer", "user": data.get("user")}


@router.get("/auth/me")
def me(request: Request):
    auth = request.headers.get("authorization") or ""
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_payload = payload.get("user") if isinstance(payload, dict) and "user" in payload else payload
    return {"id": user_payload.get("id") or user_payload.get("sub"), "email": user_payload.get("email"), "name": user_payload.get("name")}


@router.get("/auth/google")
def auth_google(request: Request):
    client_id = settings.google_client_id
    if not client_id:
        raise HTTPException(status_code=500, detail="GOOGLE_CLIENT_ID is not configured")

    redirect = settings.google_redirect_uri or str(request.base_url).rstrip("/") + "/auth/google/callback"
    scope = "openid email profile"
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect,
        "scope": scope,
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return {"auth_url": auth_url}


@router.get("/auth/google/callback")
def google_callback(code: str | None = None):
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    client_id = settings.google_client_id
    client_secret = settings.google_client_secret
    redirect = settings.google_redirect_uri

    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect,
            "grant_type": "authorization_code",
        },
    )
    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Token exchange failed")

    token_data = token_resp.json()
    access_token = token_data.get("access_token")

    userinfo_resp = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if userinfo_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    info = userinfo_resp.json()
    email = info.get("email")
    name = info.get("name")

    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")

    token = create_access_token({"sub": email, "email": email, "name": name})
    return {"access_token": token, "token_type": "bearer", "user": {"id": email, "email": email, "name": name}}
