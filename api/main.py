from typing import Optional
from starlette.responses import JSONResponse
import uvicorn

from api import configuration, access
from api.services.user_service import get_user
from api.routers import notify, token, users, oauth_google
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi import Depends
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from api.routers import analyzer
TITLE = configuration.APP_TITLE
DESCRIPTION = configuration.APP_DESCRIPTION
VERSION = configuration.APP_VERSION
app = FastAPI(
    title=TITLE,
    description=DESCRIPTION,
    version=VERSION,
    # openapi_url="/api/openapi.json",
    # docs_url="/api/docs",
    # redoc_url="/api/redoc",
)


@app.get("/api/", tags=["Index"])
def read_root():
    return {
        "title": TITLE,
        "description": DESCRIPTION,
        "version": VERSION,
    }


app.add_middleware(SessionMiddleware, secret_key=configuration.SECRET_KEY_MIDDLEWARE)
# app.include_router(oauth_basic.router, prefix="/api", tags=["Security Basic"])
app.include_router(oauth_google.router, prefix="/api/google", tags=["Security Google"])
app.include_router(token.router, prefix="/api/token", tags=["Tokens"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(notify.router, prefix="/api/notify", tags=["Notify"])
app.include_router(analyzer.router, prefix="/api", tags=["Analize"])


@app.get("/api/docs", tags=["Documentation"])  # Tag it as "documentation" for our docs
async def get_documentation(
    request: Request, user: Optional[dict] = Depends(access.get_actual_user)
):  # This dependency protects our endpoint!
    response = get_swagger_ui_html(
        openapi_url="/api/openapi.json", title="Documentation"
    )
    return response


@app.get("/api/openapi.json", tags=["Documentation"])
async def get_open_api_endpoint(
    request: Request, user: Optional[dict] = Depends(access.get_actual_user)
):  # This dependency protects our endpoint!
    response = JSONResponse(
        get_openapi(title=TITLE, version=VERSION, routes=app.routes)
    )
    return response


@app.get("/api/redoc", tags=["Documentation"])  # Tag it as "documentation" for our docs
async def redoc_html(
    request: Request, user: Optional[dict] = Depends(access.get_actual_user)
):  # This dependency protects our endpoint!
    response = get_redoc_html(openapi_url="/api/openapi.json", title="Documentation")
    return response
