
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from database import SessionLocal
from models.tag import Tag
from auth import decode_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

@router.post("/")
def create_tag(data: dict = Body(...), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    tag = Tag(name=data.get("name"), type=data.get("type"), owner_id=user["user_id"])
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return {"message": "Tag created", "tag_id": tag.id}

@router.get("/")
def list_tags(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return db.query(Tag).filter(Tag.owner_id == user["user_id"]).all()
