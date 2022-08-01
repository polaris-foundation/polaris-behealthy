from typing import Any, Dict, Optional

import requests
from requests import Response

from behealthy import config
from behealthy.utils.jwt import get_system_jwt

GDM_BFF_URL: str = f"{config.URL_BASE}/gdm-bff/gdm/v1"


def get_gdm_pdf(patient_uuid: str) -> Response:
    return requests.get(
        url=f"{GDM_BFF_URL}/pdf/{patient_uuid}",
        headers={"Authorization": f"Bearer {get_system_jwt()}"},
        timeout=30,
    )


def post_gdm_bg_readings(patient_uuid: str, bg_readings_set_data: Dict) -> Response:
    return requests.post(
        url=f"{GDM_BFF_URL}/patient/{patient_uuid}/reading",
        headers={"Authorization": f"Bearer {get_system_jwt()}"},
        json=bg_readings_set_data,
        timeout=30,
    )


def search_patient(patient_mrn: str) -> Response:
    return requests.get(
        params={
            "q": {patient_mrn},
            "active": "true",
            "locs": "static_location_uuid_L2",
        },
        url=f"{GDM_BFF_URL}/patient/search",
        headers={"Authorization": f"Bearer {get_system_jwt()}"},
        timeout=30,
    )


def create_message(message_details: Dict) -> Response:
    return requests.post(
        url=f"{GDM_BFF_URL}/message",
        headers={"Authorization": f"Bearer {get_system_jwt()}"},
        json=message_details,
        timeout=30,
    )


def get_all_sms(
    receiver: Optional[str] = None, limit: Optional[int] = None
) -> Response:
    params: Dict[str, Any] = {"receiver": receiver, "limit": limit}
    return requests.get(
        url=f"{GDM_BFF_URL}/sms",
        params=params,
        headers={"Authorization": f"Bearer {get_system_jwt()}"},
        timeout=30,
    )


def get_sms_by_uuid(sms_uuid: str) -> Response:
    return requests.get(
        url=f"{GDM_BFF_URL}/sms/{sms_uuid}",
        headers={"Authorization": f"Bearer {get_system_jwt()}"},
        timeout=30,
    )
