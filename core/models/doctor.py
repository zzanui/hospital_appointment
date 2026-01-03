from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Integer, String
from core.db import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    specialty: Mapped[str] = mapped_column(String(100),nullable=False)
