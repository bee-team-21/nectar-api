from pymongo import message
from api.models.result import Result
from api.models.user import UserInDB
from api.services.user_service import insert_or_update_user
from api.models.token import Token
from datetime import datetime, timedelta
from http.client import HTTPException

from api import configuration
from fastapi import APIRouter, status
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from google.oauth2 import id_token
from google.auth.transport import requests
from api.utils import validate_forwarded_proto
router = APIRouter()
oauth = OAuth()
CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
ACCESS_TOKEN_EXPIRE_MINUTES = configuration.ACCESS_TOKEN_EXPIRE_MINUTES
oauth.register(
    name="google",
    server_metadata_url=CONF_URL,
    client_kwargs={"scope": "openid email profile"},
    client_id=configuration.GOOGLE_CLIENT_ID,
    client_secret=configuration.GOOGLE_CLIENT_SECRET,
)


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_server_side")
    redirect_uri =  validate_forwarded_proto.validateHTTPS(url=redirect_uri, schema=request.headers.get("x-forwarded-proto"))
    print(redirect_uri)
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth", response_model=Result)
async def auth_server_side(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    accessTokenExpires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    request.session['user'] = dict(user)
    dateExpires = datetime.utcnow() + accessTokenExpires
    userDB = UserInDB(
        username=user.get("email"),
        email=user.get("email"),
        picture=user.get("picture"),
        given_name=user.get("given_name"),
        family_name=user.get("family_name"),
        disabled=False,
    )
    ret = insert_or_update_user(userDB)
    return Result(code=1, message="Login Success")
    # if ret is None:
    #     return Result(code=0, message="Account Disabled")
    # if hasattr(ret, "id"):
    #     delattr(ret, "id")
    # request.session['user'] = ret.__dict__
    # print (request.session['user'])
    # return Result(code=1, message=str(ret.__dict__))
    # accessToken = create_access_token(
    #     data={"username": user.get("email")},
    #     expires_delta=accessTokenExpires,
    #     expires_date=dateExpires,
    # )
    # return Token(
    #     access_token=accessToken,
    #     token_type="bearer",
    #     expires=accessTokenExpires,
    #     date_expires=dateExpires,
    # )


# @router.post("/auth/client", response_model=Token)
# async def auth_client_side(request: Request):
#     try:
#         body_bytes = await request.body()
#         auth_code = jsonable_encoder(body_bytes)
#         idInfo = id_token.verify_oauth2_token(
#             auth_code, requests.Request(), configuration.GOOGLE_CLIENT_ID
#         )
#         if idInfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
#             raise ValueError("Wrong issuer.")

#         accessTokenExpires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         dateExpires = datetime.utcnow() + accessTokenExpires
#         print(idInfo)
#         user = UserInDB(
#             username=idInfo.get("email"),
#             email=idInfo.get("email"),
#             picture=idInfo.get("picture"),
#             given_name=idInfo.get("given_name"),
#             family_name=idInfo.get("family_name"),
#             disabled=False,
#         )
#         ret = insert_or_update_user(user)
#         accessToken = create_access_token(
#             data={"username": user.username},
#             expires_delta=accessTokenExpires,
#             expires_date=dateExpires,
#         )
#         return Token(
#             access_token=accessToken,
#             token_type="bearer",
#             expires=accessTokenExpires,
#             date_expires=dateExpires,
#         )
#     except:
#         return HTTPException(
#             status.HTTP_400_BAD_REQUEST, "Unable to validate Google Login"
#         )


@router.get('/logout', response_model=Result)  # Tag it as "authentication" for our docs
async def logout(request: Request):
    # Remove the user
    request.session.pop('user', None)
    return Result(code=1, message="Logout Success")