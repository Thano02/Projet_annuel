from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
import os

# === RÉCUPÉRATION DES VARS D'ENV ===
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

# === INIT FASTAPI ===
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "proxy is alive"}

@app.get("/ping")
def ping():
    return {"ping": "pong"}

@app.post("/correction")
async def insert_correction(req: Request):
    try:
        data = await req.json()
        print("📥 Reçu :", data)

        # Connexion PostgreSQL
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        )
        cur = conn.cursor()

        # Insertion SQL
        cur.execute("""
            INSERT INTO corrections (timestamp, image_filename, wrong_category, corrected_category, confidence)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data["timestamp"],
            data["image_filename"],
            data["wrong_category"],
            data["corrected_category"],
            float(data["confidence"])
        ))

        conn.commit()
        cur.close()
        conn.close()

        print("✅ Insertion réussie")
        return JSONResponse(content={"status": "ok"}, status_code=200)

    except Exception as e:
        print("❌ ERREUR lors de l'insertion :", e)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )
