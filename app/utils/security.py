from datetime import datetime, timedelta, timezone
from typing import Union, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets



from app.core.config import settings

# I Use bcrypt for hashing passwords -- Industry standard
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generate a secure hash of the password using bcrypt.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with standard claims.
    
    Args:
        data: Dictionary containing token data, including 'sub' (subject)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token as string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Standard JWT clims
    to_encode = {
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "sub": str(data.get("sub")),
        "jti": secrets.token_hex(8),  # Unique identifier for the token
    }

    # I use HS256 for HMAC with SHA-256 (good balance of security and performance)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
    
def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT token to decode
        
    Returns:
        The decoded payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )    