from fastapi import APIRouter
from ..services.msk_logs_service import process_msk_logs

router = APIRouter()

@router.post("/msk/logs")
async def send_msk_logs(data: dict):
    """Process and send MSK logs to Celonis"""
    return await process_msk_logs(data)
