from pydantic import BaseModel, EmailStr


# ============================================================
# REGISTER REQUEST
# ============================================================

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


# ============================================================
# LOGIN REQUEST
# ============================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============================================================
# USER RESPONSE
# ============================================================

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


# ============================================================
# TOKEN RESPONSE
# ============================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str