from fastapi import FastAPI

from app.routers.twilio_routes import router as twilio_router
from app.routers.media_stream import router as media_router

# app = FastAPI()

# app.include_router(user_router, prefix='/api')

# @app.get("/", tags=['Root'])
# def read_root():
#     return {"message": "Welcome to the FastAPI application!"}


app = FastAPI()
app.include_router(twilio_router)
app.include_router(media_router)
