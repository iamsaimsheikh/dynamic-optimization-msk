import httpx
from fastapi import UploadFile
from ..config.celonis_client import celonis_client
from ..config.settings import get_settings
from ..utils.errors import CelonisErrors
from ..utils.utils import print_debug, handle_response
import urllib.parse


settings = get_settings()

async def fetch_data_jobs():
    """Fetch list of available data jobs"""
    endpoint = f"{settings.DATA_POOL_ID}/jobs/"
    url = f"{settings.CELO_BASE_URL}{endpoint}"

    print_debug("Fetching Data Jobs from Celonis", url)

    response = await celonis_client.get(endpoint)
    return handle_response(response)

async def create_data_job():
    """Create a new data push job"""
    endpoint = f"{settings.DATA_POOL_ID}/jobs/"
    url = f"{settings.CELO_BASE_URL}{endpoint}"

    payload = {
        "type": "REPLACE",
        "fileType": "CSV",
        "targetName": "sys_event_logs",
        "dataPoolId": settings.DATA_POOL_ID
    }

    print_debug("Creating Data Job", url, celonis_client.headers, payload)

    response = await celonis_client.post(endpoint, json=payload)
    return handle_response(response)

async def upload_csv_to_job(job_id: str, file: UploadFile):
    """Upload a CSV file to Celonis Data Push Job"""
    endpoint = f"{settings.DATA_POOL_ID}/jobs/{job_id}/chunks/upserted"
    url = f"{settings.CELO_BASE_URL}{endpoint}"

    print_debug(f"Uploading File to Job {job_id}", url)

    content = await file.read()
    files = {"file": (file.filename, content, "text/csv")}

    response = await celonis_client.post(endpoint, files=files)
    return handle_response(response)

async def execute_data_push_job(job_id: str):
    """Execute a Celonis Data Push Job"""
    endpoint = f"{settings.DATA_POOL_ID}/jobs/{job_id}"
    url = f"{settings.CELO_BASE_URL}{endpoint}"

    print_debug(f"Executing Data Push Job {job_id}", url)

    response = await celonis_client.post(endpoint)
    return {"message": f"Job execution successful for {job_id}"} if response.status_code in [200, 201] else handle_response(response)

async def get_data_push_job_status(job_id: str):
    """Get the status of a Celonis Data Push Job"""
    endpoint = f"{settings.DATA_POOL_ID}/jobs/{job_id}"
    url = f"{settings.CELO_BASE_URL}{endpoint}"

    print_debug(f"Checking Status of Data Push Job {job_id}", url)

    response = await celonis_client.get(endpoint)
    return handle_response(response)

async def execute_data_model_load(data_model_id: str):
    """Execute a Celonis Data Model Load Job"""

    # ✅ Encode user input safely
    safe_data_model_id = urllib.parse.quote(data_model_id)

    url = (
        "https://academic-celonis-snfll0.eu-2.celonis.cloud/"
        "integration/api/v1/data-pools/{}/data-models/{}/load"
    ).format(settings.DATA_POOL_ID, safe_data_model_id)

    headers = {
        "Authorization": "Bearer {}".format(settings.CELO_API_KEY),
        "Content-Type": "application/json"
    }

    print_debug("Executing Data Model Load", url, headers)

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)

    return handle_response(response)
