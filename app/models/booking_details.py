from sqlalchemy import Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.core.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Link to the hotel
    hotel_id: Mapped[int] = mapped_column(Integer, ForeignKey("hotels.id"), nullable=False)
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="bookings")

    user_name: Mapped[str] = mapped_column(String(128), nullable=False)  

