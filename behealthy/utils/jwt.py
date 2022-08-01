import datetime
from typing import Optional

import requests

from behealthy import config

JANITOR_URL: str = f"{config.URL_BASE}/dhos-janitor/dhos/v1"


class JWTCache:
    token: Optional[str] = None
    expiry: Optional[datetime.datetime] = None


def get_system_jwt() -> str:
    if (
        JWTCache.token is None
        or JWTCache.expiry is None
        or JWTCache.expiry - datetime.datetime.utcnow() < datetime.timedelta(minutes=5)
    ):
        response = requests.get(f"{JANITOR_URL}/system/dhos-robot/jwt")
        response.raise_for_status()
        response_body = response.json()

        JWTCache.token = response_body["jwt"]
        JWTCache.expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    return str(JWTCache.token)
