import random
from app.services.hotel_service import get_hotels_by_location
from sqlalchemy.ext.asyncio import AsyncSession


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



# def book_hotel(hotel_name: str):
#     for hotel in HOTELS:
#         if hotel["name"].lower() == hotel_name.lower():
#             return {
#                 "status": "confirmed",
#                 "hotel": hotel,
#                 "message": f"Your booking for {hotel['name']} is confirmed at ${hotel['price']}."
#             }
#     return {"status": "failed", "reason": "Hotel not found", "message": f"Could not find {hotel_name}."}


