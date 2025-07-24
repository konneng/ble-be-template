
from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
