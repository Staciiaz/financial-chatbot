from contextlib import asynccontextmanager

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount

from ..config.app import AppConfig
from ..containers import Container
from .api import APIServer
from .api.middlewares.error import ErrorMiddleware


class Server:
    def __init__(self):
        """
        Initialize the server and its components.
        """
        self.config = AppConfig()
        self.container = Container(self.config)
        self.api_server = APIServer(self.container)
    
    @asynccontextmanager
    async def lifespan(self, app: Starlette):
        """
        Manage the server's lifecycle, including startup and shutdown.
        """
        await self.container.initialize()
        yield
        await self.container.close()

    def start(self):
        """
        Start the HTTP server.
        """
        app = Starlette(
            routes=[
                Mount("/api", app=self.api_server.get_asgi_app()),
            ],
            lifespan=self.lifespan,
            middleware=[
                Middleware(
                    CORSMiddleware,
                    allow_origins=["*"],
                    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                    allow_headers=["Authorization", "Content-Type"],
                ),
                Middleware(ErrorMiddleware),
            ]
        )

        uvicorn.run(app, host=self.config.host, port=self.config.port)
