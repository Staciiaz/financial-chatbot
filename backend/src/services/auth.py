from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from ..config.app import AppConfig
from ..models.user import User
from ..repositories.user import UserRepository


class AuthService:
    def __init__(
        self,
        config: AppConfig,
        user_repo: UserRepository,
    ):
        self.config = config
        self.user_repo = user_repo

    def generate_jwt_token(self, payload: dict) -> str:
        return jwt.encode(
            {
                **payload,
                "exp": datetime.now(UTC) + timedelta(minutes=3), # Set token expiration time to 3 minutes
            },
            self.config.jwt_secret_key,
            algorithm="HS256",
        )
    
    def validate_jwt_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.config.jwt_secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    async def register(self, username: str, password: str, company: str, sector: str) -> None:
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # Create a new user
        user = User(
            username=username,
            password_hash=password_hash,
            company=company,
            sector=sector,
        )
        await self.user_repo.create_user(user)

    async def login(self, username: str, password: str) -> str:
        # Retrieve the user from the database
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            raise ValueError("Invalid username or password")

        # Verify the password
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            raise ValueError("Invalid username or password")

        # Generate a JWT token
        token = self.generate_jwt_token(user.model_dump())
        return token
