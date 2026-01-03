from fastapi import FastAPI

app = FastAPI(title="Derm Clinic - Gateway", version="0.1.0")

@app.get("/ping")
def ping():
    return {"service": "gateway", "message": "pong2"}
