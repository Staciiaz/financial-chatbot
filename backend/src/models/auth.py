from pydantic import BaseModel


class AuthLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
