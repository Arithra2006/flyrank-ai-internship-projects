from fastapi import APIRouter, Depends

from auth.dependencies import verify_token


router = APIRouter(
    tags=["Protected Routes"]
)


# -----------------------------
# Public Route
# -----------------------------

@router.get("/public/info")
def public_info():

    return {
        "message": "Welcome stranger! This info is public."
    }



# -----------------------------
# Protected Profile Route
# -----------------------------

@router.get("/protected/profile")
def profile(
    user = Depends(verify_token)
):

    return {
        "message": "Welcome to your private profile",
        "user": {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at
        }
    }



# -----------------------------
# Protected Dashboard Route
# -----------------------------

@router.get("/protected/dashboard")
def dashboard(
    user = Depends(verify_token)
):

    return {
        "message": "Welcome to your dashboard",
        "user_id": user.id
    }