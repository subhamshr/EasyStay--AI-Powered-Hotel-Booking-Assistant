from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.hotel import Hotel
from app.models.booking_details import Booking
from datetime import datetime, timezone


async def get_hotel_by_name(session: AsyncSession, hotel_name: str):
    result = await session.execute(
        select(Hotel).where(Hotel.name.ilike(f"%{hotel_name}%"))
    )
    return result.scalars().first()

async def get_hotels_by_location(session: AsyncSession, location: str):
    query = select(Hotel).where(Hotel.location.ilike(f"%{location}%"))
    result = await session.execute(query)
    return result.scalars().all()

async def create_booking(session:AsyncSession,hotel_id: int, user_name: str):
    new_booking = Booking(
    hotel_id=hotel_id,
    user_name=user_name,
)
    session.add(new_booking)
    await session.commit()


