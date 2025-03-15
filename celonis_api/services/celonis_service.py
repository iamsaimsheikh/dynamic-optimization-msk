import aiofiles
import httpx
from fastapi import UploadFile
from ..config.celonis_client import celonis_client, data_push_client
from ..config.settings import get_settings

settings = get_settings()

async def fetch_data_jobs():
    """Fetch list of available data jobs"""
    endpoint = f"{settings.DATA_POOL_ID}/jobs/"
    url = f"{settings.CELO_BASE_URL}{endpoint}"

    print(f"\n🔍 DEBUG: Fetching Data Jobs from Celonis")
    print(f"📌 URL: {url}")

    response = await celonis_client.get(endpoint)

    print(f"📥 Response Status: {response.status_code}")
    print(f"📥 Response Body: {response.text}")

    return response.json() if response.status_code == 200 else {
        "error": "Failed to fetch data jobs",
        "status_code": response.status_code,
        "response": response.text
    }

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

    print(f"\n🔍 DEBUG: Creating Data Job")
    print(f"📌 URL: {url}")
    print(f"📄 Headers: {celonis_client.headers}")
    print(f"📊 Payload: {payload}")

    response = await celonis_client.post(endpoint, json=payload)

    print(f"📥 Response Status: {response.status_code}")
    print(f"📥 Response Body: {response.text}")

    return response.json() if response.status_code in [200, 201] else {
        "error": "Failed to create data job",
        "status_code": response.status_code,
        "response": response.text
    }

async def upload_csv_to_job(job_id: str, file: UploadFile):
    """Upload a CSV file to Celonis Data Push Job"""

    endpoint = f"{settings.DATA_POOL_ID}/jobs/{job_id}/chunks/upserted"
    url = f"{settings.CELO_BASE_URL}{endpoint}"

    print(f"\n🔍 DEBUG: Uploading File to Job {job_id}")
    print(f"📌 URL: {url}")

    content = await file.read()
    files = {"file": (file.filename, content, "text/csv")}

    print(f"📄 Headers: {celonis_client.headers}")

    response = await celonis_client.post(endpoint, files=files)

    print(f"📥 Response Status: {response.status_code}")
    print(f"📥 Response Body: {response.text}")

    # ✅ Fix: Check if response has content before parsing JSON
    if response.status_code in [200, 201]:
        return response.json() if response.content else {"message": "File uploaded successfully"}

    return {
        "error": "Failed to upload file",
        "status_code": response.status_code,
        "response": response.text
    }


async def execute_data_push_job(job_id: str):
    """Execute a Celonis Data Push Job"""

    endpoint = f"{settings.DATA_POOL_ID}/jobs/{job_id}"  # Ensure correct endpoint
    url = f"{settings.CELO_BASE_URL}{endpoint}"

    print(f"\n🔍 DEBUG: Executing Data Push Job {job_id}")
    print(f"📌 URL: {url}")
    print(f"📄 Headers: {celonis_client.headers}")

    response = await celonis_client.post(endpoint)

    print(f"📥 Response Status: {response.status_code}")

    # ✅ If there's no response body but status is successful, return success message
    if response.status_code in [200, 201]:
        print("✅ File upload successful")
        return {"message": f"Job execution successful for {job_id}"}

    # ✅ Handle other status codes properly
    return {
        "error": "Failed to execute data push job",
        "status_code": response.status_code,
        "response": response.text if response.content else "No response body"
    }


async def get_data_push_job_status(job_id: str):
    """Get the status of a Celonis Data Push Job"""

    endpoint = f"{settings.DATA_POOL_ID}/jobs/{job_id}"  # Ensure correct endpoint
    url = f"{settings.CELO_BASE_URL}{endpoint}"

    print(f"\n🔍 DEBUG: Checking Status of Data Push Job {job_id}")
    print(f"📌 URL: {url}")
    print(f"📄 Headers: {celonis_client.headers}")

    response = await celonis_client.get(endpoint)

    print(f"📥 Response Status: {response.status_code}")

    # ✅ Handle successful response
    if response.status_code == 200:
        try:
            job_status = response.json()
            print(f"✅ Job Status: {job_status}")
            return job_status
        except json.JSONDecodeError:
            print("❌ Failed to parse JSON response")
            return {
                "error": "Invalid JSON response from Celonis API",
                "status_code": response.status_code,
                "response": response.text
            }

    # ✅ Handle errors
    return {
        "error": "Failed to fetch job status",
        "status_code": response.status_code,
        "response": response.text if response.content else "No response body"
    }


async def execute_data_model_load(pool_id: str ,data_model_id: str):
    """Execute a Celonis Data Model Load Job"""

    url = (f"https://academic-celonis-snfll0.eu-2.celonis.cloud/"
           f"integration/api/v1/data-pools/{settings.DATA_POOL_ID}/"
           f"data-models/{data_model_id}/load")

    headers = {
        "Authorization": f"Bearer {settings.CELO_API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"\n🔍 DEBUG: Executing Data Model Load for {data_model_id}")
    print(f"📌 URL: {url}")
    print(f"📄 Headers: {headers}")

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)

    print(f"📥 Response Status: {response.status_code}")

    if response.status_code not in [200, 201, 204]:
        print("❌ Job execution failed")
        return {
            "error": "Failed to execute data model load job",
            "status_code": response.status_code,
            "response": response.text if response.text else "No response body"
        }

    try:
        response_json = response.json() if response.text else {}
    except json.JSONDecodeError:
        print("❌ Failed to parse JSON response")
        return {
            "error": "Invalid JSON response from Celonis API",
            "status_code": response.status_code,
            "response": response.text
        }

    print(f"📥 Response Body: {response_json}")
    return {"message": f"Data model load job executed successfully for data model id: {data_model_id}"}



