from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import UserStoryGroup
from pydantic import BaseModel

storyrouter = APIRouter()

class UserStory(BaseModel):
    userid: int
    app: str          # "todo" or "blog"
    azureid: int
    title: str
    description: str


@storyrouter.get("/retrievestory")
async def get_user_stories(userid: int, db: Session = Depends(get_db)):
    groups = db.query(UserStoryGroup).filter(
        UserStoryGroup.userid == userid
    ).all()

    result = []

    for g in groups:
        result.append({
            "id": g.id,
            "app": g.app,
            "stories": g.stories  # this is already a JSON list
        })

    return {"success": True, "groups": result}


@storyrouter.post("/addstory")
async def create_story(user_story: UserStory, db: Session = Depends(get_db)):

    # Check if story group exists
    story_group = db.query(UserStoryGroup).filter(
        UserStoryGroup.userid == user_story.userid,
        UserStoryGroup.app == user_story.app
    ).first()

    # If no group exists → create one
    if not story_group:
        story_group = UserStoryGroup(
            userid=user_story.userid,
            app=user_story.app,
            stories=[]
        )
        db.add(story_group)
        db.commit()
        db.refresh(story_group)

    # Check if story already exists by title or azureid
    for s in story_group.stories:
        if s["title"] == user_story.title or s["azure_id"] == user_story.azureid:
            return {"error": "Story already exists"}

    # Add new story to JSON list
    new_story = {
        "azure_id": user_story.azureid,
        "title": user_story.title,
        "description": user_story.description,
    }

    story_group.stories.append(new_story)

    db.commit()
    db.refresh(story_group)

    return {
        "success": True,
        "message": "Story added",
        "stories": story_group.stories
    }

# @storyrouter.delete("/createapplication")
