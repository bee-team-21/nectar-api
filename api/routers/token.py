from typing import List, Optional
from starlette.responses import JSONResponse, Response
from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder

from api.models.user import UserInDB
from api.models.token import Token
from api.models.result import Result
from api.access import get_actual_user
from api.services import token_service
from api.validators.mongo import PyObjectId
from api.utils.responses import get_error_message, KEYS_ERROR

router = APIRouter()


@router.get("", response_model=List[Token], status_code=status.HTTP_200_OK)
async def get_token(
    user: Optional[UserInDB] = Depends(get_actual_user), q: Optional[str] = None
):
    search = Token(token="", username=user.username)
    if q is not None:
        search.token = q
        slacks = token_service.search(item=search)
    else:
        slacks = token_service.get(search.username)
    return slacks


@router.post("", response_model=Token, status_code=status.HTTP_201_CREATED)
async def post_token(user: Optional[UserInDB] = Depends(get_actual_user)):
    item = Token(token="",username=user.username)
    print (item)
    item.username_insert = user.username
    ret = token_service.create(item)
    item.id = ret.inserted_id
    ret = token_service.getByIDAndUser(item)
    return ret


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Result},
        status.HTTP_204_NO_CONTENT: {"model": None},
        status.HTTP_400_BAD_REQUEST: {"model": Result},
    },
)
async def delete_token(
    id: PyObjectId, user: Optional[UserInDB] = Depends(get_actual_user)
):
    item = Token(token="", username=user.username)
    item.id = id
    if item.id is None:
        result = jsonable_encoder(get_error_message(key=KEYS_ERROR.id_not_found))
        return JSONResponse(content=result, status_code=status.HTTP_404_NOT_FOUND)

    ret = token_service.getByIDAndUser(item)
    if ret is None:
        result = jsonable_encoder(get_error_message(key=KEYS_ERROR.object_not_found))
        return JSONResponse(content=result, status_code=status.HTTP_404_NOT_FOUND)

    item.username_update = user.username
    ret = token_service.delete(item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
