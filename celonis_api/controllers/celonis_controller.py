from fastapi import APIRouter, HTTPException, UploadFile, File
from ..services.celonis_service import (
    fetch_data_jobs,
    create_data_job,
    upload_csv_to_job,
    execute_data_push_job,
    get_data_push_job_status,
    execute_data_model_load
)

router = APIRouter()

@router.get("/celonis/datajobs")
async def get_data_jobs():
    """Fetch list of available data jobs from Celonis"""
    result = await fetch_data_jobs()
    
    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return result

@router.post("/celonis/datajobs")
async def post_data_job():
    """Create a new data job in Celonis"""
    result = await create_data_job()
    
    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result)

    return result

@router.post("/celonis/datajobs/{job_id}/upload")
async def post_upload_csv(job_id: str, file: UploadFile = File(...)):
    """Upload CSV file to a Celonis data push job"""
    result = await upload_csv_to_job(job_id, file)

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return result

@router.post("/celonis/datajobs/{job_id}/execute")
async def post_execute_data_push_job(job_id: str):
    """Execute a Celonis Data Push Job"""
    result = await execute_data_push_job(job_id)

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return result

@router.get("/celonis/datajobs/{job_id}/status")
async def get_job_status(job_id: str):
    """
    API endpoint to fetch the status of a Celonis Data Push Job.
    """
    result = await get_data_push_job_status(job_id)
    return result

@router.post("/celonis/data-models/{data_model_id}/load")
async def post_execute_data_model_load(data_model_id: str):
    """
    Trigger a Celonis Data Model Load Job.
    """
    result = await execute_data_model_load(data_model_id)

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return result
