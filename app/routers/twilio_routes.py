from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Connect

router = APIRouter()

@router.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    response = VoiceResponse()
    response.say("Welcome to the AI Hotel Booking Assistant!")
    response.pause(length=1)
    response.say("You can ask me to search hotels or book a hotel.")

    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f"wss://{host}/media-stream")
    response.append(connect)

    return HTMLResponse(content=str(response), media_type="application/xml")


