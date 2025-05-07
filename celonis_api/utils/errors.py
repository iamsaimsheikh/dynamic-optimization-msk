from enum import Enum

class CelonisErrors(Enum):
    FETCH_JOBS_FAILED = "Failed to fetch data jobs"
    CREATE_JOB_FAILED = "Failed to create data push job"
    UPLOAD_FAILED = "Failed to upload file"
    EXECUTION_FAILED = "Failed to execute data push job"
    STATUS_FETCH_FAILED = "Failed to fetch job status"
    INVALID_JSON = "Invalid JSON response from Celonis API"
