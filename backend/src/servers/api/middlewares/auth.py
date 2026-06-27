from httpx import request
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from ....services.auth import AuthService


class AuthMiddleware:
    def __init__(self, app: ASGIApp, auth_svc: AuthService):
        self.app = app
        self.auth_svc = auth_svc

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            request = Request(scope)

            try:
                authorization = request.headers.get("Authorization")
                if not authorization:
                    raise ValueError("Missing Authorization header")

                token_type, token = authorization.split()
                if token_type.lower() != "bearer":
                    raise ValueError("Invalid token type")
                
                session_id, payload = await self.auth_svc.validate_token(token)
                scope["authenticated"] = {
                    "session_id": session_id,
                    "username": payload.get("username"),
                }
            except Exception as e:
                response = JSONResponse(
                    content={"message": "Invalid or expired token", "error": str(e)},
                    status_code=401, # Unauthorized
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)
