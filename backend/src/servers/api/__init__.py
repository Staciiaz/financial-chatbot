from fastapi import APIRouter, Depends, FastAPI
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Mount

from ...containers import Container
from .controllers.agent import AgentController
from .controllers.auth import AuthController
from .controllers.migration import MigrationController
from .middlewares.auth import AuthMiddleware


class APIServer:
    def __init__(
        self,
        container: Container,
    ):
        self.public_api = FastAPI()
        self.protected_api = FastAPI()
        self.auth_svc = container.auth_svc
        self.auth_ctrl = AuthController(container.auth_svc)
        self.migration_ctrl = MigrationController(container.migration_svc)
        self.agent_ctrl = AgentController(container.agent_svc)
        self.setup_routes()

    def setup_routes(self):
        """
        Setup the routes for the API server.
        """
        migration = APIRouter(prefix="/migration")
        migration.add_api_route("/import-pinecone-index", self.migration_ctrl.import_pinecone_index, methods=["POST"])
        self.public_api.include_router(migration)

        auth = APIRouter(prefix="/auth")
        auth.add_api_route("/register", self.auth_ctrl.register, methods=["POST"])
        auth.add_api_route("/login", self.auth_ctrl.login, methods=["POST"])
        auth.add_api_route("/logout", self.auth_ctrl.logout, methods=["POST"])
        auth.add_api_route("/refresh", self.auth_ctrl.refresh, methods=["POST"])
        self.public_api.include_router(auth)

        agent = APIRouter(prefix="/agent")
        agent.add_api_route("/ask-question", self.agent_ctrl.ask_question, methods=["GET"])
        self.protected_api.include_router(agent)

    def get_asgi_app(self):
        """
        Get the ASGI application instance.

        :return: The ASGI application instance.
        """
        return Starlette(
            routes=[
                Mount("/protected", app=self.protected_api, middleware=[Middleware(AuthMiddleware, auth_svc=self.auth_svc)]),
                Mount("/", app=self.public_api),
            ]
        )
