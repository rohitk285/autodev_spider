from sqlalchemy import Integer,Column,String,ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Story(Base):
    __tablename__="stories"

    id = Column(Integer,primary_key=True,index=True)
    azure_id = Column(Integer,unique=True,index=True)
    title = Column(String)
    description = Column(String)

    userid = Column(Integer,ForeignKey("users.id"))

    owner = relationship("User",back_populates="stories")