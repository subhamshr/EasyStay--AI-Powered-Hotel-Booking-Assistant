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
    
    