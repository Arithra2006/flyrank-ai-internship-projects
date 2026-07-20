from fastapi import APIRouter, HTTPException, status, Header

from models.user import SignupRequest, LoginRequest
from auth.supabase_client import supabase


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# -----------------------------
# Signup
# -----------------------------

@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED
)
def signup(user: SignupRequest):

    try:
        response = supabase.auth.sign_up(
            {
                "email": user.email,
                "password": user.password
            }
        )

        return {
            "message": "User created successfully",
            "user": response.user
        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# -----------------------------
# Login
# -----------------------------

@router.post("/login")
def login(user: LoginRequest):

    try:

        response = supabase.auth.sign_in_with_password(
            {
                "email": user.email,
                "password": user.password
            }
        )


        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": response.user
        }


    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials"
        )


# -----------------------------
# Logout
# -----------------------------

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT
)
def logout(
    authorization: str = Header(None)
):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )


    token = authorization.replace(
        "Bearer ",
        ""
    )


    try:

        supabase.auth.sign_out()

        return


    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )