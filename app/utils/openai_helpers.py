from app.utils.booking_functions import search_hotels
import os
import json
import base64
import asyncio
import websockets
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream
from dotenv import load_dotenv
from fastapi.responses import Response
from app.core.database import AsyncSessionLocal  # your SQLAlchemy async session factory
from app.utils.booking_functions import book_hotel



async def handle_search_hotels(openai_ws, call_id, function_args):
    print("=== HANDLE_SEARCH_HOTELS CALLED ===")
    print(f"call_id: {call_id}")
    print(f"function_args: {function_args}")
    
    location = function_args['location']
    print(f"Extracted location: {location}")
    
    async with AsyncSessionLocal() as session:
        search_result = await search_hotels(session, location)


    print(f"Search result: {search_result['summary']}")

    await openai_ws.send(json.dumps({
    "type": "function_call.output",
    "call_id": call_id,
    "output": json.dumps(search_result) 
}))
    await openai_ws.send(json.dumps({
        "type": "response.create",
        "response": {
            "modalities": ["text", "audio"],
             "instructions": f"Say exactly: '{search_result['summary']}'"

        }
    }))
    

async def handle_book_hotel(openai_ws, call_id, function_args,session):
    print("=== HANDLE_SEARCH_HOTELS CALLED ===")
    print(f"call_id: {call_id}")
    print(f"function_args: {function_args}")

    hotel_name=function_args['hotel_name']
    user_name = function_args.get("user_name", "Guest")
    print(f"Extracted hotel name: {hotel_name}")

    booking_result = await book_hotel(session, hotel_name, user_name)
    print(f"Booking result: {booking_result}")
    await openai_ws.send(json.dumps({
    "type": "function_call.output",
    "call_id": call_id,
    "output": json.dumps(booking_result)  # or search_result['summary'] if you want just the text
}))
    await openai_ws.send(json.dumps({
        "type": "response.create",
        "response": {
            "modalities": ["text", "audio"],
             "instructions": f"Say exactly: '{booking_result['message']}'"

        }
    }))
