from datetime import datetime
from pymongo.collection import ReturnDocument
from api.database import db
from api.models.token import Token
from api.utils.currentmillis import current
from jose import jws
from api.configuration import STATIC_SECRET
SECRET = STATIC_SECRET

def create(item: Token):
    item.date_insert = datetime.utcnow()
    item.disabled = False
    if hasattr(item, "date_update"):
        delattr(item, "date_update")
    if hasattr(item, "id"):
        delattr(item, "id")
    if hasattr(item, "username_update"):
        delattr(item, "username_update")
    payload = {"username": item.username, "current": current()}
    item.token = jws.sign(payload, SECRET, algorithm="HS256")
    ret = db.token.insert_one(item.dict(by_alias=True))
    return ret


def delete(item: Token):
    item.date_update = datetime.utcnow()
    ret = db.token.find_one_and_update(
        {"_id": item.id, "username": item.username, "disabled": False},
        {
            "$set": {
                "disabled": True,
                "date_update": item.date_update,
                "username_update": item.username_update,
            }
        },
        return_document=ReturnDocument.AFTER,
    )
    return ret


def getByID(item: Token):
    finded = db.token.find_one({"_id": item.id, "disabled": False})
    if finded is not None:
        return Token(**finded)
    else:
        return None


def getByIDAndUser(item: Token):
    finded = db.token.find_one(
        {"_id": item.id, "username": item.username, "disabled": False}
    )
    if finded is not None:
        return Token(**finded)
    else:
        return None


def getToken(item: Token):
    finded = db.token.find_one({"disabled": False, "token": item.token})
    if finded is None:
        return None
    else:
        return finded

def get(username: str):
    finded = db.token.find({"disabled": False, "username": username})
    items = []
    for find in finded:
        items.append(Token(**find))
    return items


def search(item: Token):
    finded = db.token.find(
        {
            "$and": [
                {"disabled": False},
                {"username": item.username},
                {"token": {"$regex": item.token}},
            ]
        }
    )
    slacks = []
    for find in finded:
        slacks.append(Token(**find))
    return slacks
