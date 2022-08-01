import requests

from behealthy import config
from behealthy.utils.jwt import get_system_jwt

AGGREGATOR_URL: str = f"{config.URL_BASE}/dhos-aggregator/dhos/v1"


def process_syne_bg_readings() -> requests.Response:
    return requests.post(
        url=f"{AGGREGATOR_URL}/process_syne_bg_readings",
        headers={"Authorization": f"Bearer {get_system_jwt()}"},
        timeout=30,
    )
