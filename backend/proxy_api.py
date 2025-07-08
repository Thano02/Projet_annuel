# proxy_api.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

app = FastAPI()

# Autoriser tout le monde (ou restreindre plus tard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

# Connexion PostgreSQL
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

@app.post("/correction")
async def insert_correction(req: Request):
    try:
        data = await req.json()
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, dbname=PG_DB,
            user=PG_USER, password=PG_PASSWORD
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO corrections (timestamp, image_filename, wrong_category, corrected_category, confidence, bbox)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data["timestamp"],
            data["image_filename"],
            data["wrong_category"],
            data["corrected_category"],
            float(data["confidence"]),
            str(data["bbox"])
        ))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def read_root():
    return {"status": "ok", "message": "proxy is alive"}

@app.get("/ping")
def ping():
    return {"ping": "pong"}