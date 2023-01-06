from pydantic import BaseSettings, BaseModel
import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from keycloak import KeycloakOpenID
from pathlib import Path

logger = logging.getLogger("hellokeycloak")


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8080

    keycloak_server_url: str = "http://localhost:8090/"
    keycloak_realm: str = "cloudportal"
    keycloak_client_id: str = "hellokeycloak"

    class Config:
        env_file = ".env"


settings = Settings()
keycloak_openid = KeycloakOpenID(
    server_url=settings.keycloak_server_url,
    client_id=settings.keycloak_client_id,
    realm_name=settings.keycloak_realm,
)
keycloak_key = (
    "-----BEGIN PUBLIC KEY-----\n"
    + keycloak_openid.public_key()
    + "\n-----END PUBLIC KEY-----"
)

base_path = Path(__file__).resolve().parent
app = FastAPI()
app.mount("/static", StaticFiles(directory=base_path / "static"), name="static")
templates = Jinja2Templates(directory=base_path / "templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str
    roles: dict[str, list[str]]


async def get_current_user(token: str = Depends(oauth2_scheme)):
    options = {"verify_signature": True, "verify_aud": False, "verify_exp": True}
    token_data = keycloak_openid.decode_token(token, key=keycloak_key, options=options)
    return User(
        username=token_data["preferred_username"],
        email=token_data["email"],
        roles={k: v["roles"] for (k, v) in token_data["resource_access"].items()},
    )


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "keycloak_server_url": settings.keycloak_server_url,
            "keycloak_realm": settings.keycloak_realm,
            "keycloak_client_id": settings.keycloak_client_id,
        },
    )


@app.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


def run():
    uvicorn.run("hellokeycloak.main:app", host=settings.host, port=settings.port)


if __name__ == "__main__":
    run()
