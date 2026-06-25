from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    company: Mapped[str] = mapped_column(nullable=False)
    sector: Mapped[str] = mapped_column(nullable=False)
