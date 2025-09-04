import random
from app.services.hotel_service import get_hotels_by_location
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.hotel_service import get_hotel_by_name,create_booking

async def search_hotels(session: AsyncSession, location: str):
    hotels = await get_hotels_by_location(session, location)

    if not hotels:
        return {"hotels": [], "summary": f"No hotels found in {location}"}

    hotels_list = [
        {
            "id": hotel.id,
            "name": hotel.name,
            "price": float(hotel.price) + random.randint(-10, 10)    # simulate dynamic pricing
        }
        for hotel in hotels
    ]

    summary = f"I found these hotels in {location}: "
    summary += ", ".join(f"{h['name']} for ${h['price']}" for h in hotels_list)

    return {"hotels": hotels_list, "summary": summary}



async def book_hotel(session: AsyncSession, hotel_name: str, user_name: str):
    """Full booking workflow: find hotel and create booking."""
    hotel = await get_hotel_by_name(session, hotel_name)
    if not hotel:
        return {"status": "failed", "message": f"Hotel '{hotel_name}' not found."}

    booking = await create_booking(session, hotel.id, user_name)
    return {
        "status": "confirmed",
        "hotel_name": hotel.name,
        "message": f"Your booking for '{hotel.name}' is confirmed."
    }

