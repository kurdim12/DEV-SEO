"""
FastAPI dependencies for database sessions, authentication, and authorization.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
import httpx

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User


# HTTP Bearer token security
security = HTTPBearer()

# JWKS cache at module level - fetched once per process lifetime, refreshed on key rotation
_jwks_cache: Optional[dict] = None


async def _get_clerk_jwks() -> dict:
    """Fetch Clerk JWKS with simple in-memory caching."""
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            settings.CLERK_JWKS_URL,
            timeout=10.0,
        )
        resp.raise_for_status()
        _jwks_cache = resp.json()
    return _jwks_cache


async def _decode_clerk_token(token: str) -> dict:
    """
    Verify a Clerk RS256 JWT against the JWKS endpoint.
    Retries once on kid mismatch to handle key rotation.
    """
    global _jwks_cache

    for attempt in range(2):
        jwks = await _get_clerk_jwks()
        try:
            # jose can accept a JWKS dict directly as `key` when algorithms=["RS256"]
            payload = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                options={"verify_aud": False},  # Clerk tokens have no `aud` by default
            )
            return payload
        except JWTError as exc:
            if attempt == 0 and "kid" in str(exc).lower():
                # Key may have rotated — clear cache and retry
                _jwks_cache = None
                continue
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="JWT validation failed"
    )


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt (12 rounds)."""
    # Bcrypt has a 72-byte limit on passwords
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password."""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Payload data to encode in the token

    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string to decode

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer credentials from request header
        db: Database session

    Returns:
        Authenticated User object

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = decode_token(token)

    # Verify token type
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID
    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Parse user ID as UUID
    try:
        user_id = UUID(user_id_str)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_clerk(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user from Clerk JWT token.

    Validates Clerk JWT tokens and automatically provisions users.

    Args:
        credentials: HTTP Bearer credentials from request header
        db: Database session

    Returns:
        Authenticated User object

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials

    try:
        payload = await _decode_clerk_token(token)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    # Extract Clerk user ID
    clerk_id: Optional[str] = payload.get("sub")
    if not clerk_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract email and name from token (might not be present in Clerk tokens)
    email: Optional[str] = payload.get("email")
    name: Optional[str] = payload.get("name") or payload.get("given_name")

    # If email is not in token, fetch from Clerk API
    if not email:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.clerk.com/v1/users/{clerk_id}",
                    headers={"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"},
                )
                if response.status_code == 200:
                    user_data = response.json()
                    email = user_data.get("email_addresses", [{}])[0].get("email_address")
                    if not name:
                        name = user_data.get("first_name") or user_data.get("username")
        except Exception:
            pass  # Silently fail, will raise error below if email is still missing

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing email and failed to fetch from Clerk",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Look up user by Clerk ID
    result = await db.execute(select(User).where(User.clerk_id == clerk_id))
    user = result.scalar_one_or_none()

    if not user:
        # Auto-provision user if they don't exist
        user = User(
            clerk_id=clerk_id,
            email=email,
            name=name,
            password_hash=None,  # Clerk users don't need password hash
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # Update email/name if changed in Clerk
        updated = False
        if user.email != email:
            user.email = email
            updated = True
        if name and user.name != name:
            user.name = name
            updated = True

        if updated:
            await db.commit()
            await db.refresh(user)

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get the current active user.
    Can be extended to check if user is disabled/banned.

    Args:
        current_user: Current authenticated user

    Returns:
        Active User object

    Raises:
        HTTPException: If user is inactive
    """
    # Add additional checks here if needed (e.g., is_active flag)
    return current_user
