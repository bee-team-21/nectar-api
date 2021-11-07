from fastapi import APIRouter, status, Response
from fastapi.params import Depends
from api.access import get_api_key
from api.models.forbidden import Forbidden
from api.models.analysis_result import AnalysisResult
from api.models.result import Result
from fastapi.openapi.models import APIKey
from api.services.cognitive_consult import get_analyze
from api.utils.responses import KEYS_ERROR, KEYS_SUCCESS, get_error_message

router = APIRouter()


@router.post(
    "/analyze",
    responses={
        status.HTTP_403_FORBIDDEN: {"model": Forbidden},
        status.HTTP_404_NOT_FOUND: {"model": Result},
    },
)
async def post_analyze(url:str, user: APIKey = Depends(get_api_key)):
    res = get_analyze(url,user.get('username'))
    return res