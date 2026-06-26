from typing import Annotated

from fastapi import Body, Header

from ....services.auth import AuthService
from .dto import AuthLoginDTO, AuthRegisterDTO


class AuthController:
    def __init__(
        self,
        auth_svc: AuthService,
    ):
        self.auth_svc = auth_svc

    async def register(
        self,
        api_key: Annotated[str, Header(min_length=6, max_length=100)],
        dto: Annotated[AuthRegisterDTO, Body()],
    ):
        await self.auth_svc.register(
            username=dto.username,
            password=dto.password,
            company=dto.company,
            sector=dto.sector,
            secret_key=api_key,
        )
        return {"message": "Registration successful"}

    async def login(
        self,
        dto: Annotated[AuthLoginDTO, Body()],
    ):
        token = await self.auth_svc.login(
            username=dto.username,
            password=dto.password,
        )
        return {"message": "Login successful", "token": token}
