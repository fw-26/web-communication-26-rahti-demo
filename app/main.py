from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
from app.db import get_conn, create_schema

app = FastAPI()

origins = ["*"] # Change to the real front end origin in production

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_schema()

class Booking(BaseModel):
    guest_id: int
    room_id: int
    datefrom: date
    dateto: date

# Main route for this API
@app.get("/")
def read_root(): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT version() ")
        result = cur.fetchone()

    return { "msg": f"Hotel API!", "db_status": result }

# if-statements
@app.get("/if/{term}")
def if_test(term: str):
    msg = "Default msg"

    if (term == "hello" 
        or term == "hi"):
        msg = "Hello yourself!"
    elif (term == "hej" or term == "moi") and 1 == 0:
        msg = "Hej på dig!" 
    else:
        msg = f"I don't understand {term}"

    return { "msg": msg}


# List all rooms 
@app.get("/rooms")
def get_rooms(): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM rooms")
        rooms = cur.fetchall()
    return rooms

# Get one room
@app.get("/rooms/{id}")
def get_one_room(id: int): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT * 
            FROM rooms 
            WHERE id = %s
        """, (id,)) # <- tuple, list is also fine: [id]
        room = cur.fetchone()
    return room

# Create booking
@app.post("/bookings")
def create_booking(booking: Booking):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO bookings (
                room_id, 
                guest_id,
                datefrom,
                dateto
            ) VALUES (
                %s, %s, %s, %s
            ) RETURNING id
        """, [
            booking.room_id, 
            booking.guest_id,
            booking.datefrom,
            booking.dateto
        ])
        new_booking = cur.fetchone()
        
    return { 
        "msg": "Booking created!", 
        "id": new_booking['id']
    }




