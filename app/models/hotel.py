from sqlalchemy import Integer, String, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from datetime import datetime
from app.core.database import Base
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship



class Hotel(Base):
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    location: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking", 
        back_populates="hotel", 
        cascade="all, delete-orphan"
    )
