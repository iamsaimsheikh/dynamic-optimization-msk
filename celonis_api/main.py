from fastapi import FastAPI
from celonis_api.controllers import celonis_controller, msk_logs_controller

app = FastAPI(title="Celonis & MSK API")

app.include_router(celonis_controller.router, prefix="/api", tags=["Celonis"])
app.include_router(msk_logs_controller.router, prefix="/api", tags=["MSK Logs"])

@app.get("/")
async def root():
    return {"message": "Celonis API is running"}
 