from fastapi import APIRouter, status, Response
from fastapi.params import Depends
from api.access import get_api_key
from api.models.forbidden import Forbidden
from api.models.notify import Notify
from api.models.result import Result
from fastapi.openapi.models import APIKey
from api.utils.notify import send_notify
from api.utils.responses import KEYS_ERROR, KEYS_SUCCESS, get_error_message

router = APIRouter()


@router.post(
    "/notify",
    responses={
        status.HTTP_403_FORBIDDEN: {"model": Forbidden},
        status.HTTP_404_NOT_FOUND: {"model": Result},
    },
)
async def post_notify(item: Notify, user: APIKey = Depends(get_api_key)):
    res = send_notify(item)
    if res is None:
        return get_error_message(key=KEYS_ERROR.send_notify)
    else:
        return get_error_message(key=KEYS_SUCCESS.send_notify)