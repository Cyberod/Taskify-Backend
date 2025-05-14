from typing import Optional
from pydantic import BaseModel, Field

class Token(BaseModel):
    """
    Token schema for OAuth2 authentication response.
    
    Attributes:
        access_token: JWT token
        token_type: Type of token (bearer)
        expires_in: Token expiration time in seconds
    """
    access_token: str = Field(..., description="JWT Access Token")
    token_type: str = Field(..., description="Type of the token (bearer)")
    expires_in: int = Field(..., description="Token expiration time in seconds")
   

class TokenPayload(BaseModel):
    """
    Token payload schema for JWT token contents.
    
    Attributes:
        sub: Subject (user ID)
        exp: Expiration time (Unix timestamp)
    """
    sub: Optional[int] = Field(None, description="Subject (user ID) of the token")  
    exp: Optional[int] = Field(None, description="Expiration time of the token")


