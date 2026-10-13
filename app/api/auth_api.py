import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import get_current_user, require_admin
from app.schemas import ApiResponse, UserRegister
from app.services.auth_service import create_access_token, hash_password, verify_password
from app.services.db_service import create_user, get_user_by_email, get_user_by_id, get_connection

router = APIRouter(prefix="/auth", tags=["Auth"])


def public_user(user):
    return {key: user[key] for key in ("id", "email", "role", "is_active", "created_at")}


@router.post("/register", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def register(request: UserRegister):
    try:
        user = create_user(email=request.email, password_hash=hash_password(request.password))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already registered")
    return {"code": 201, "message": "Registered", "data": {"user": public_user(user), "access_token": create_access_token(user["id"], user["role"]), "token_type": "bearer"}}


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form.username.strip().lower())
    if not user or not user["is_active"] or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    return {"access_token": create_access_token(user["id"], user["role"]), "token_type": "bearer", "user": public_user(user)}


@router.get("/me", response_model=ApiResponse)
def me(user=Depends(get_current_user)):
    return {"code": 200, "message": "success", "data": public_user(user)}


@router.get("/users", response_model=ApiResponse)
def users(admin=Depends(require_admin)):
    with get_connection() as conn:
        items = [public_user(dict(row)) for row in conn.execute("SELECT * FROM users ORDER BY created_at DESC")]
    return {"code": 200, "message": "success", "data": items}


@router.patch("/users/{user_id}/active", response_model=ApiResponse)
def set_active(user_id: str, active: bool, admin=Depends(require_admin)):
    if user_id == admin["id"]:
        raise HTTPException(status_code=400, detail="Cannot change your own active status")
    with get_connection() as conn:
        result = conn.execute("UPDATE users SET is_active = ? WHERE id = ?", (int(active), user_id))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
    return {"code": 200, "message": "success", "data": public_user(get_user_by_id(user_id))}
