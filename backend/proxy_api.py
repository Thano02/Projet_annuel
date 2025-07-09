from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from datetime import datetime
import os
import traceback

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

DB_CONFIG = {
    "host": os.getenv("PGHOST", ""),
    "port": os.getenv("PGPORT", "5432"),
    "dbname": os.getenv("PGDATABASE", ""),
    "user": os.getenv("PGUSER", ""),
    "password": os.getenv("PGPASSWORD", "")
}

@app.post("/correction")
async def receive_correction(req: Request):
    try:
        payload = await req.json()
        print("📥 Reçu :", payload)

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO corrections (timestamp, image_filename, wrong_category, corrected_category, confidence)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            payload["timestamp"],
            payload["image_filename"],
            payload["wrong_category"],
            payload["corrected_category"],
            payload["confidence"]
        ))
        conn.commit()
        cur.close()
        conn.close()

        return {"status": "ok"}
    except Exception as e:
        print("❌ ERREUR lors de l'insertion :", e)
        traceback.print_exc()  # 👈 pour afficher le détail dans Render
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/ping")
async def ping():
    return {"ping": "pong"}
