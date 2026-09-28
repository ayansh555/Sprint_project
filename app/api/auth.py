from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse,
)

from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    try:
        print("REGISTER: request received")

        # ----------------------------------------------------
        # Check username
        # ----------------------------------------------------

        existing_username = (
            db.query(User)
            .filter(User.username == request.username)
            .first()
        )

        print("REGISTER: username checked")

        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # ----------------------------------------------------
        # Check email
        # ----------------------------------------------------

        existing_email = (
            db.query(User)
            .filter(User.email == request.email)
            .first()
        )

        print("REGISTER: email checked")

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # ----------------------------------------------------
        # Create user ID
        # ----------------------------------------------------

        user_id = f"USER-{uuid4().hex[:12]}"

        # ----------------------------------------------------
        # Hash password
        # ----------------------------------------------------

        password_hash = hash_password(
            request.password
        )

        print("REGISTER: password hashed")

        # ----------------------------------------------------
        # Create user
        # ----------------------------------------------------

        user = User(
            user_id=user_id,
            username=request.username,
            email=request.email,
            password_hash=password_hash
        )

        db.add(user)

        print("REGISTER: user added")

        # ----------------------------------------------------
        # Save to database
        # ----------------------------------------------------

        db.commit()

        print("REGISTER: commit successful")

        # ----------------------------------------------------
        # Refresh user
        # ----------------------------------------------------

        db.refresh(user)

        print("REGISTER: refresh successful")

        return user

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        print("========================================")
        print("REGISTER ERROR:", repr(e))
        print("========================================")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Find user by email
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # --------------------------------------------------------
    # Verify password
    # --------------------------------------------------------

    if not verify_password(
        request.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # --------------------------------------------------------
    # Create JWT token
    # --------------------------------------------------------

    access_token = create_access_token(
        {
            "sub": user.user_id,
            "username": user.username,
            "email": user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ============================================================
# GET CURRENT USER FROM TOKEN
# ============================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Decode JWT
    # --------------------------------------------------------

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # --------------------------------------------------------
    # Get user ID
    # --------------------------------------------------------

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


# ============================================================
# CURRENT USER
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):

    return current_user