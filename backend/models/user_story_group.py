from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class UserStoryGroup(Base):
    __tablename__ = "user_story_groups"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(Integer, ForeignKey("users.id"))
    app = Column(String, index=True)          # "todo" | "blog"
    stories = Column(JSON)                    # List of stories as JSON array

    owner = relationship("User", back_populates="story_groups")
