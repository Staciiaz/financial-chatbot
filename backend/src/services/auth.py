import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal

import bcrypt
import jwt

from ..config.app import AppConfig
from ..infrastructures.redis import RedisClient
from ..models.auth import AuthLoginResponse
from ..models.user import User
from ..repositories.user import UserRepository
from ..types import UnauthorizedError

TokenType = Literal["access", "refresh"]


class AuthService:
    def __init__(
        self,
        config: AppConfig,
        redis: RedisClient,
        user_repo: UserRepository,
    ):
        self.config = config
        self.redis = redis.get_client()
        self.user_repo = user_repo
        self.token_types = {
            "access": (self.config.jwt.access_token_secret, timedelta(minutes=3)),  # Set token expiration time to 3 minutes
            "refresh": (self.config.jwt.refresh_token_secret, timedelta(days=1)),  # Set token expiration time to 1 day
        }

    def _generate_token(
        self,
        payload: dict,
        token_type: TokenType = "access",
    ) -> tuple[str, int]:
        if token_type not in self.token_types:
            raise ValueError("Invalid token type")
        
        secret, expiration = self.token_types[token_type]
        token = jwt.encode(
            payload={
                **payload,
                "exp": datetime.now(tz=UTC) + expiration,
            },
            key=secret, algorithm="HS256",
        )
        return token, int(expiration.total_seconds())
    
    async def validate_token(
        self, 
        token: str,
        token_type: TokenType = "access",
    ) -> tuple[str, dict]:
        try:
            if token_type not in self.token_types:
                raise ValueError("Invalid token type")
            
            secret, _ = self.token_types[token_type]
            payload = jwt.decode(token, key=secret, algorithms=["HS256"])
            session_id = payload.get("session_id")
            if not session_id:
                raise UnauthorizedError(f"Invalid {token_type} token")
            
            # Check if the session exists in Redis
            session = await self.redis.hgetall(f"session:{session_id}")
            if not session:
                raise UnauthorizedError("Session expired")
            
            # Check if the provided access token matches the one stored in Redis
            if session.get(f"{token_type}_token") != token:
                raise UnauthorizedError(f"Invalid {token_type} token")
            
            return session_id, session
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Token has expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedError("Invalid token")

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

    async def login(self, username: str, password: str) -> AuthLoginResponse:
        # Retrieve the user from the database
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            raise UnauthorizedError("Invalid username or password")

        # Verify the password
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            raise UnauthorizedError("Invalid username or password")
        
        # Generate a new session ID and tokens
        session_id = str(uuid.uuid4())
        jwt_payload = {"session_id": session_id}
        access_token, access_expires_in = self._generate_token(jwt_payload, token_type="access")
        refresh_token, refresh_expires_in = self._generate_token(jwt_payload, token_type="refresh")

        # Store the session in Redis with an expiration time
        pipe = self.redis.pipeline()
        pipe.hset(f"session:{session_id}", mapping={
            "username": str(user.username),
            "access_token": access_token,
            "refresh_token": refresh_token,
        })
        pipe.expire(f"session:{session_id}", refresh_expires_in)  # Set expiration for the session
        await pipe.execute()

        return AuthLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=access_expires_in,
        )
    
    async def logout(self, refresh_token: str) -> None:
        # Validate the refresh token
        session_id, payload = await self.validate_token(refresh_token, token_type="refresh")
        if not session_id:
            raise UnauthorizedError("Invalid refresh token")

        # Delete the session from Redis
        await self.redis.delete(f"session:{session_id}")

    async def refresh_token(self, refresh_token: str) -> AuthLoginResponse:
        # Validate the refresh token
        session_id, session = await self.validate_token(refresh_token, token_type="refresh")

        # Generate new tokens and update the session in Redis
        jwt_payload = {"session_id": session_id}
        new_access_token, new_access_expires_in = self._generate_token(jwt_payload, token_type="access")
        new_refresh_token, new_refresh_expires_in = self._generate_token(jwt_payload, token_type="refresh")
        pipe = self.redis.pipeline()
        pipe.hset(f"session:{session_id}", mapping={
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        })
        pipe.expire(f"session:{session_id}", new_refresh_expires_in)  # Update expiration for the session
        await pipe.execute()
        
        return AuthLoginResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=new_access_expires_in,
        )
