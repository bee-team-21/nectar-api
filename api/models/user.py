from typing import Optional
from pydantic import BaseModel, Field
from api.validators.mongo import PyObjectId
from bson import ObjectId
from datetime import datetime


class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    username: str
    email: Optional[str] = None
    picture: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    disabled: Optional[bool] = None
    admin:  Optional[bool] = False
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserInDB(User):
    hashed_password: Optional[str] = None
    date_insert: Optional[datetime] = None
    date_update: Optional[datetime] = None
