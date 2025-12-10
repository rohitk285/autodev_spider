from fastapi import APIRouter, Depends
from models import Story
from pydantic import BaseModel
from database import get_db
from sqlalchemy.orm import Session

class UserStory(BaseModel):
    userid : int
    title : str
    description : str
    azureid : int

storyrouter = APIRouter()

@storyrouter.get("/retrievestory")
async def getuserstories(
    userid:int,
    db : Session = Depends(get_db)):

    userstories = db.query(Story).filter(Story.userid == userid).all()
    
    return {"success":"link hitting","story":userstories}

@storyrouter.post("/addstory")
async def createstory(
    user_story : UserStory,
    db : Session = Depends(get_db)):

    existing = db.query(Story).filter(Story.userid == user_story.userid,Story.title == user_story.title).first()

    if existing:
        return {"failed updating" : "Story already exists"}
    
    new_Story = Story(
        userid = user_story.userid,
        azure_id = user_story.azureid,
        title = user_story.title,
        description = user_story.description,
    )

    db.add(new_Story)
    db.commit()
    db.refresh(new_Story)

    return {"success" : "added story","story" : new_Story}