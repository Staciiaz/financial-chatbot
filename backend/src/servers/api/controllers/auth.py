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
        dto: Annotated[AuthRegisterDTO, Body()],
    ):
        await self.auth_svc.register(
            username=dto.username,
            password=dto.password,
            company=dto.company,
            sector=dto.sector,
        )
        return {"message": "Registration successful"}

    async def login(
        self,
        dto: Annotated[AuthLoginDTO, Body()],
    ):
        response = await self.auth_svc.login(
            username=dto.username,
            password=dto.password,
        )
        return {"message": "Login successful", "data": response}
    
    async def logout(
        self,
        authorization: Annotated[str, Header(min_length=8, pattern=r"^Bearer\s.+")],
    ):
        await self.auth_svc.logout(authorization[7:]) # Remove "Bearer " prefix
        return {"message": "Logout successful"}

    async def refresh(
        self,
        authorization: Annotated[str, Header(min_length=8, pattern=r"^Bearer\s.+")],
    ):
        response = await self.auth_svc.refresh_token(authorization[7:]) # Remove "Bearer " prefix
        return {"message": "Token refreshed successfully", "data": response}
