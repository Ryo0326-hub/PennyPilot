from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Optional
from urllib.request import urlopen

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

bearer_scheme = HTTPBearer(auto_error=False)


def _auth_disabled() -> bool:
    return os.getenv("AUTH_REQUIRED", "true").strip().lower() != "true"


def _allow_test_header() -> bool:
    configured = os.getenv("ALLOW_TEST_AUTH_HEADER")
    if configured is not None:
        return configured.strip().lower() == "true"

    # Default to enabled only in non-production to make local integration easier.
    environment = os.getenv("ENVIRONMENT", "development").strip().lower()
    return environment != "production"


def _is_production() -> bool:
    return os.getenv("ENVIRONMENT", "development").strip().lower() == "production"


@lru_cache(maxsize=1)
def _get_auth_config() -> tuple[Optional[str], Optional[str], Optional[str]]:
    issuer = os.getenv("AUTH_ISSUER") or os.getenv("AUTH0_ISSUER_BASE_URL")
    jwks_url = os.getenv("AUTH_JWKS_URL")
    audience = os.getenv("AUTH_AUDIENCE") or os.getenv("AUTH0_AUDIENCE")

    auth0_domain = os.getenv("AUTH0_DOMAIN")
    if not issuer and auth0_domain:
        issuer = auth0_domain if auth0_domain.startswith("http") else f"https://{auth0_domain}"

    if not jwks_url and issuer:
        normalized = issuer.rstrip("/")
        jwks_url = f"{normalized}/.well-known/jwks.json"

    return issuer, jwks_url, audience


@lru_cache(maxsize=1)
def _fetch_jwks() -> dict:
    _, jwks_url, _ = _get_auth_config()
    if not jwks_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth misconfiguration",
        )

    try:
        with urlopen(jwks_url, timeout=5) as response:  # nosec B310
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify authentication token",
        ) from exc


def _get_signing_key(token: str) -> dict:
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        ) from exc

    kid = unverified_header.get("kid")
    if not kid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    jwks = _fetch_jwks()
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token",
    )


def _decode_token(token: str) -> str:
    issuer, _jwks_url, audience = _get_auth_config()
    key = _get_signing_key(token)

    options = {"verify_aud": bool(audience)}
    decode_kwargs = {
        "key": key,
        "algorithms": ["RS256"],
        "options": options,
    }
    if audience:
        decode_kwargs["audience"] = audience
    if issuer:
        decode_kwargs["issuer"] = issuer

    try:
        payload = jwt.decode(token, **decode_kwargs)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        ) from exc

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    return str(subject)


def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    x_test_user_id: Optional[str] = Header(default=None, alias="X-Test-User-Id"),
) -> str:
    if _allow_test_header():
        if x_test_user_id:
            return x_test_user_id
        if not _is_production():
            # Local fallback when frontend auth token exchange is not ready yet.
            return "local-dev-user"

    if _auth_disabled():
        return "local-dev-user"

    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    return _decode_token(credentials.credentials)
