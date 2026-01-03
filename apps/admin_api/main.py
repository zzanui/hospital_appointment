from fastapi import FastAPI

app = FastAPI(title="Derm Clinic - Admin API", version="0.1.0")

@app.get("/ping")
def ping():
    return {"service": "admin_api", "message": "pong"}
