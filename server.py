from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
CORS(app)

# Path to the folder where server.py is
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_URL = "postgresql://neondb_owner:npg_KOD6MZS2kNlI@ep-plain-lab-ae27j4wa-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_conn():
    return psycopg2.connect(DB_URL)

# Serve index.html
@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")

# Serve any other file in the same directory
@app.route("/<path:filename>")
def serve_file(filename):
    return send_from_directory(BASE_DIR, filename)

@app.post("/reserve")
def reserve():
    booking = request.json
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM reservations WHERE date=%s AND time=%s",
                        (booking["date"], booking["time"]))
            if cur.fetchone():
                return jsonify({"error": "This slot is already booked."}), 400

            cur.execute("""
                INSERT INTO reservations (name, phone, email, date, time, people)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """, (booking["name"], booking["phone"], booking["email"],
                  booking["date"], booking["time"], booking["people"]))
            booking_id = cur.fetchone()["id"]
            conn.commit()

    booking["id"] = booking_id
    return jsonify({"message": "Booking confirmed!", "reservation": booking})

@app.get("/reservations")
def get_reservations():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM reservations")
            return jsonify(cur.fetchall())

@app.delete("/reservation/<int:booking_id>")
def delete_reservation(booking_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM reservations WHERE id=%s", (booking_id,))
            conn.commit()
            if cur.rowcount == 0:
                return jsonify({"error": "Reservation not found"}), 404
    return jsonify({"message": "Reservation canceled"})

if __name__ == "__main__":
    import threading
    import webbrowser
    def open_browser():
        webbrowser.open("http://localhost:5000")
    threading.Timer(1.5, open_browser).start()
    app.run(debug=True)
