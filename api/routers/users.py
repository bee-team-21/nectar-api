from fastapi import APIRouter, Depends
from api.models.user import User
# from api.token import get_current_active_user
from api.access import get_actual_user

router = APIRouter()


@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_actual_user)):
    return current_user
