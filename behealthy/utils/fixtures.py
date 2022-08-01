import uuid
from typing import Any, Dict

from requests import Response
from she_data_generation.location import location_factory
from she_data_generation.observation import observation_set_factory
from she_data_generation.patient import patient_factory
from she_http_clients.encounters import EncountersApiClient
from she_http_clients.locations import LocationsApiClient
from she_http_clients.services import ServicesApiClient

from behealthy import config


def create_location() -> Dict[str, Any]:
    client = LocationsApiClient(base_url=config.URL_BASE)
    location_data = location_factory(product_name="SEND")()
    response: Response = client.create_location(location_data=location_data)
    return response.json()


def create_patient(location_id: str) -> Dict[str, Any]:
    client = ServicesApiClient(base_url=config.URL_BASE)
    patient_data = patient_factory(locations=[location_id], product_name="SEND")()
    response: Response = client.create_patient(
        patient_data=patient_data, product_name="SEND"
    )
    return response.json()


def create_encounter(
    location_id: str, patient_record_id: str, dh_product_id: str, patient_id: str
) -> Dict[str, Any]:
    client = EncountersApiClient(base_url=config.URL_BASE)
    encounter_data = {
        "location_uuid": location_id,
        "epr_encounter_id": str(uuid.uuid4()),
        "encounter_type": "INPATIENT",
        "admitted_at": "2018-01-01T00:00:00.000Z",
        "discharged_at": "2018-01-01T00:00:00.000Z",
        "patient_record_uuid": patient_record_id,
        "patient_uuid": patient_id,
        "dh_product_uuid": dh_product_id,
    }
    response: Response = client.create_encounter(encounter_data=encounter_data)
    return response.json()


def create_observation_set() -> Dict[str, Any]:
    return observation_set_factory()()
