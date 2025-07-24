
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from passlib.context import CryptContext
from auth import create_access_token, create_refresh_token, create_reset_token, decode_token

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(data: dict = Body(...), db: Session = Depends(get_db)):
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_context.hash(password)
    user = User(email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered", "user_id": user.id}

@router.post("/login")
def login(data: dict = Body(...), db: Session = Depends(get_db)):
    email = data.get("email")
    password = data.get("password")
    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "access_token": create_access_token({"sub": user.email, "user_id": user.id}),
        "refresh_token": create_refresh_token({"sub": user.email, "user_id": user.id}),
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(data: dict = Body(...)):
    token = data.get("refresh_token")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return {
        "access_token": create_access_token({"sub": payload["sub"], "user_id": payload["user_id"]})
    }

@router.post("/change-password")
def change_password(data: dict = Body(...), db: Session = Depends(get_db)):
    email = data.get("email")
    current = data.get("current_password")
    new = data.get("new_password")
    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(current, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid current password")
    user.hashed_password = pwd_context.hash(new)
    db.commit()
    return {"message": "Password updated"}

@router.post("/reset-password-request")
def reset_request(data: dict = Body(...), db: Session = Depends(get_db)):
    email = data.get("email")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    reset_token = create_reset_token({"sub": user.email, "user_id": user.id})
    return {"reset_token": reset_token}

@router.post("/reset-password-confirm")
def reset_confirm(data: dict = Body(...), db: Session = Depends(get_db)):
    token = data.get("reset_token")
    new_password = data.get("new_password")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    user.hashed_password = pwd_context.hash(new_password)
    db.commit()
    return {"message": "Password reset successful"}
