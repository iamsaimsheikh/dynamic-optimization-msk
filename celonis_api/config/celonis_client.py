import httpx
from ..config.settings import get_settings

settings = get_settings()

# Celonis API clients
celonis_client = httpx.AsyncClient(
    base_url=settings.CELO_BASE_URL,
    headers={"Authorization": f"AppKey {settings.CELO_API_KEY}"}
)

data_push_client = httpx.AsyncClient(
    base_url=settings.CELO_BASE_URL,
    headers={"Authorization": f"AppKey {settings.DATA_PUSH_API_KEY}"}
)
