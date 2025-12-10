from fastapi import APIRouter,Depends
from pydantic import BaseModel
from models import User as UserModel
from database import get_db
from sqlalchemy.orm import Session


authrouter = APIRouter()

class UserRegister(BaseModel):
    username : str
    email : str
    password : str

class UserSignin(BaseModel):
    username : str
    password : str


class User(BaseModel):
    username : str
    email : str
    id : int
    class Config:
        from_attributes = True

@authrouter.get("/")
def auth():
    return {"success" : "valid route"}

@authrouter.post("/register")
async def register_user(
    user_data : UserRegister,
    db : Session = Depends(get_db)):

    oldusername = db.query(UserModel).filter(UserModel.username == user_data.username).first()
    oldemail = db.query(UserModel).filter(UserModel.email == user_data.email).first()

    if oldusername or oldemail:
        return {"failed" : "username or email already exists"}

    new_user = UserModel(
        username = user_data.username,
        email = user_data.email,
        hashed_password = user_data.password,
        is_active = True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"email" : user_data.email , "username" : user_data.username,"msg" : "new record created","id":new_user}

@authrouter.post("/signin")
async def user_signin(
    user_data : UserSignin,
    db : Session = Depends(get_db)):

    dbusername = db.query(UserModel).filter(UserModel.username == user_data.username, UserModel.hashed_password == user_data.password).first()

    if not dbusername:
        return {"failed" : "incorrect username or password"}
    
    return {"success" : "login success","username" : user_data.username}
