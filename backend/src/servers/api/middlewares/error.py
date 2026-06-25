import orjson
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class ErrorMiddleware:
    """
    Middleware to handle exceptions and return a JSON response with error details.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            try:
                # Intercept the response messages to check for exceptions
                intercept_messages: list[Message] = []
                should_intercept = True

                async def send_wrapper(message: Message):
                    nonlocal should_intercept, intercept_messages
                    if message["type"] == "http.response.start" and message["status"] == 500:
                        should_intercept = False

                    if should_intercept:
                        intercept_messages.append(message)

                await self.app(scope, receive, send_wrapper)

                # After successful execution, send the intercepted messages
                for message in intercept_messages:
                    await send(message)
            except Exception as e:
                # Handle the exception and return a JSON response
                # Potential improvement: can separate the status code by exception type
                response = JSONResponse(
                    content={"message": "Internal Server Error", "error": str(e)},
                    status_code=500,
                )
                await response(scope, receive, send)
        else:
            await self.app(scope, receive, send)