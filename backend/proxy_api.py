from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test pour Render
@app.get("/")
def root():
    return {"status": "ok", "message": "proxy is alive"}

@app.get("/ping")
def ping():
    return {"ping": "pong"}

@app.post("/correction")
async def insert_correction(req: Request):
    try:
        correction = await req.json()
        print("📥 Reçu :", correction)

        conn = psycopg2.connect(
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"),
            dbname=os.getenv("PG_DB"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD")
        )
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO corrections (timestamp, image_filename, wrong_category, corrected_category, confidence)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                correction["timestamp"],
                correction["image_filename"],
                correction["wrong_category"],
                correction["corrected_category"],
                correction["confidence"]
            )
        )
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Insertion réussie")
        return JSONResponse(content={"status": "ok"})

    except Exception as e:
        print("❌ ERREUR lors de l'insertion :", e)
        return JSONResponse(status_code=500, content={"message": str(e)})
