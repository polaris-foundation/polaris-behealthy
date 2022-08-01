from typing import Dict

import requests
from requests import Response

from behealthy import config
from behealthy.utils.jwt import get_system_jwt

SEND_BFF_URL: str = f"{config.URL_BASE}/send-bff/send/v1"


def create_send_observation_set(observation_set_data: Dict) -> Response:
    return requests.post(
        url=f"{SEND_BFF_URL}/observation_set",
        headers={"Authorization": f"Bearer {get_system_jwt()}"},
        json=observation_set_data,
        timeout=30,
    )


def get_send_observation_sets_by_encounter_id(encounter_id: str) -> Response:
    return requests.get(
        url=f"{SEND_BFF_URL}/observation_set",
        headers={"Authorization": f"Bearer {get_system_jwt()}"},
        params={"encounter_id": encounter_id},
        timeout=30,
    )


def search_location_for_encounters(location_uuid: str) -> Response:
    return requests.get(
        url=f"{SEND_BFF_URL}/encounter/search",
        headers={"Authorization": f"Bearer {get_system_jwt()}"},
        params={"location": location_uuid},
        timeout=30,
    )


def search_patient_encounters(mrn: str) -> Response:
    return requests.get(
        url=f"{SEND_BFF_URL}/encounter/search",
        headers={"Authorization": f"Bearer {get_system_jwt()}"},
        params={"q": mrn},
        timeout=30,
    )


def get_ward_list() -> Response:
    return requests.get(
        url=f"{SEND_BFF_URL}/location/patient/summary?location_type=225746001",
        headers={"Authorization": f"Bearer {get_system_jwt()}"},
        timeout=30,
    )


def get_encounters_by_patient_id(patient_uuid: str) -> Response:
    params: Dict = {
        "patient_id": patient_uuid,
        "open_as_of": "1970-01-01T00:00:00.000Z",
        "show_deleted": True,
    }
    return requests.get(
        url=f"{SEND_BFF_URL}/encounter",
        headers={"Authorization": f"Bearer {get_system_jwt()}"},
        params=params,
        timeout=30,
    )
