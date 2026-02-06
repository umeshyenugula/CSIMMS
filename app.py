from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from datetime import datetime, time
from dotenv import load_dotenv
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
import pytz
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all (for hackathon)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
load_dotenv()
MONGO_URL = os.getenv("MONGO_URI")
if not MONGO_URL:
    raise ValueError("ERROR: MONGO_URI not found in .env file")
client = MongoClient(MONGO_URL)
db = client["meal_system"]
participants = db["participants"]
IST = pytz.timezone("Asia/Kolkata")
def get_meal_slot():
    now = datetime.now(IST).time()   
    if time(12, 0) <= now <= time(14, 0):
        return "meal_lunch_day1"
    if time(19, 0) <= now <= time(22, 0):
        return "meal_dinner_day1"
    if time(8, 0) <= now <= time(10, 0):
        return "meal_breakfast_day2"
    if time(12, 0) <= now <= time(14, 0):
        return "meal_lunch_day2"
    return None
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return FileResponse("static/Index.html")
@app.get("/verify/{qr_code}")
def verify(qr_code: str):
    user = participants.find_one({"_id": qr_code})
    if not user:
        return {"status": "invalid", "message": "Invalid Code"}
    meal_slot = get_meal_slot()
    if not meal_slot:
        return {"status": "not_time", "message": "Meal Not Available Now"}
    if user.get(meal_slot):
        return {"status": "claimed", "message": "Meal Already Taken"}
    participants.update_one({"_id": qr_code}, {"$set": {meal_slot: True}})
    return {
        "status": "success",
        "message": "Meal Provided",
        "student_name": user["student_name"],
        "team_name": user["team_name"],
        "college": user["college"]
    }
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

