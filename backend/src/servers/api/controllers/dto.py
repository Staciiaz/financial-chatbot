from pydantic import BaseModel, Field


class AuthRegisterDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    company: str = Field(..., min_length=2, max_length=100)
    sector: str = Field(..., min_length=2, max_length=50)


class AuthLoginDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
