from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.hotel import Hotel
from datetime import datetime, timezone


async def get_hotel_names(session: AsyncSession):
    query = select(Hotel)
    result = await session.execute(query)
    return result.scalars().all()

async def get_hotels_by_location(session: AsyncSession, location: str):
    query = select(Hotel).where(Hotel.location.ilike(f"%{location}%"))
    result = await session.execute(query)
    return result.scalars().all()



