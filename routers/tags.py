
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.tag import Tag

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_tag(name: str, type: str, owner_id: int, db: Session = Depends(get_db)):
    tag = Tag(name=name, type=type, owner_id=owner_id)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return {"message": "Tag created", "tag_id": tag.id}

@router.get("/")
def list_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()
