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
from fastapi.responses import Response
from app.utils.openai_helpers import handle_search_hotels,handle_book_hotel
from fastapi import APIRouter, WebSocket
from app.core.config import settings
from app.core.database import AsyncSessionLocal

OPENAI_API_KEY=settings.OPENAI_API_KEY
VOICE = 'alloy'
OPENAI_REALTIME_MODEL = "gpt-4o-realtime-preview-2024-10-01"

router = APIRouter()

@router.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    async with websockets.connect(
        'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
        extra_headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
    ) as openai_ws:
    
        await send_session_update(openai_ws)
        stream_sid = None
        
        async def receive_from_twilio():
            """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
            nonlocal stream_sid
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media' and openai_ws.open:
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data['media']['payload']
                        }
                        await openai_ws.send(json.dumps(audio_append))
                    elif data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        # print(f"Incoming stream has started {stream_sid }")
            except WebSocketDisconnect:
                print("Client disconnected.")
                if openai_ws.open:
                    await openai_ws.close()

        async def send_to_twilio():
            nonlocal stream_sid
            
            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)
           
                    print("OpenAI message received:", response) 
                    # Handle audio deltas
                    if response['type'] == 'response.audio.delta' and response.get('delta'):
                        audio_payload = response['delta']  
                        audio_delta = {
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {"payload": audio_payload}
                        }
                        await websocket.send_json(audio_delta)
                    
                    if response['type'] == 'response.function_call_arguments.done':
    # Model is requesting a function call
                        function_name = response['name']
                        function_args = json.loads(response['arguments'])
                        print(function_name,function_args)
                        async with AsyncSessionLocal() as session:
                            if function_name == "search_hotels":
                                await handle_search_hotels(openai_ws, response['call_id'], function_args)
                            elif function_name == "book_hotel":
                                await handle_book_hotel(openai_ws, response['call_id'], function_args, session)
                        

            except Exception as e:
                print(f"Error in send_to_twilio: {e}")


        await asyncio.gather(receive_from_twilio(), send_to_twilio())
        
        
# async def send_session_update(openai_ws):
#     """
#     Send session update to OpenAI Realtime API.
#     Ensures the model only uses search_hotels and book_hotel functions.
#     """
#     session_update = {
#         "type": "session.update",
#         "session": {
#             "turn_detection": {"type": "server_vad"},
#             "input_audio_format": "g711_ulaw",
#             "output_audio_format": "g711_ulaw",
#             "voice": VOICE,
#             "instructions": (
#                 "You are a hotel booking AI assistant. "
#                 "Do NOT answer user requests directly. "
#                 "Always call the provided functions (search_hotels and book_hotel) to handle any user request. "
#                 "Only speak to confirm that a function has been called or to read back the function's results."
#                  "Only speak after the function call has returned results."
#             ),
#             "modalities": ["text", "audio"],
#             "temperature": 0.8,
#             "tools": [
#                 {
#                      "type": "function",
#                     "name": "search_hotels",
#                     "description": "Search for hotels in a specific location",
#                     "parameters": {
#                         "type": "object",
#                         "properties": {
#                             "location": {"type": "string"}
#                         },
#                         "required": ["location"]
#                     }
#                 },
#                 {
#                      "type": "function",
#                     "name": "book_hotel",
#                     "description": "Book a hotel for the user",
#                     "parameters": {
#                         "type": "object",
#                         "properties": {
#                             "hotel_name": {"type": "string"},
#                             "nights": {"type": "integer"}
#                         },
#                         "required": ["hotel_name", "nights"]
#                     }
#                 }
#             ]
#         }
#     }
                                     
#     await openai_ws.send(json.dumps(session_update))
#     print("✅ Session updated with tools and instructions")

    # initial_response = {
    #     "type": "response.create",
    #     "response": {
    #         "instructions": (
    #             "You are ready to handle hotel search and booking requests. "
    #             "Always call the appropriate function (search_hotels or book_hotel) for any user query."
    #         ),
    #         "modalities": ["text","audio"]
    #     }
    # }
    # await openai_ws.send(json.dumps(initial_response))
    # print("✅ Sent initial response.create")
                         


async def send_session_update(openai_ws):
    """
    Send session update to OpenAI Realtime API.
    Ensures the model only uses search_hotels and book_hotel functions.
    """
    # 1️Session update with tools & instructions
    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "server_vad"},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": VOICE,
            "instructions": (
                "You are a hotel booking AI assistant. "
                "Do NOT answer user requests directly. "
                "Always call the provided functions (search_hotels and book_hotel) to handle any user request. "
                "Only speak to confirm that a function has been called or to read back the function's results."
                 "Only speak after the function call has returned results."
            ),
            "modalities": ["text", "audio"],
            "temperature": 0.8,
            "tools": [
                {
                     "type": "function",
                    "name": "search_hotels",
                    "description": "Search for hotels in a specific location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"}
                        },
                        "required": ["location"]
                    }
                },
                {
                     "type": "function",
                    "name": "book_hotel",
                    "description": "Book a hotel for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "hotel_name": {"type": "string"},
                            "nights": {"type": "integer"},
                            "guest_name": {"type": "string"}
                        },
                        "required": ["hotel_name", "nights","guest_name"]
                    }
                }
            ]
        }
    }

    await openai_ws.send(json.dumps(session_update))
    print("✅ Session updated with tools and instructions")



