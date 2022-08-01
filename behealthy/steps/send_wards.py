import uuid
from typing import Dict, List

import draymed
from behave import given, then
from behave.runner import Context
from she_data_generation.encounter import encounter_factory
from she_data_generation.location import location_factory
from she_logging import logger

from behealthy.clients import send_bff_client


@given(
    "I have a {location_type} location {location_prefix} which is a child of {parent_prefix}"
)
def create_location_with_parent(
    context: Context, location_type: str, location_prefix: str, parent_prefix: str
) -> None:
    if not hasattr(context, "uuid"):
        context.uuid = str(uuid.uuid4())

    location_uuid = (location_prefix + context.uuid)[:36]
    location_generator = location_factory(product_name="SEND")
    location_data = location_generator()
    if parent_prefix != "nobody":
        parent_uuid = (parent_prefix + context.uuid)[:36]
        location_data["parent"] = parent_uuid

    location_data["location_type"] = draymed.codes.code_from_name(
        name=location_type, category="location"
    )
    location_data["uuid"] = location_uuid
    location = context.locations_client.create_location(location_data).json()
    context.location = location
    context.clues.append(("I have a ward", location))
    context.locations_cleanup.append(location["uuid"])
    logger.debug("the location is %s" % location)


@given("has an open encounter at {location_prefix}")
def create_open_encounter(context: Context, location_prefix: str) -> None:
    location_uuid = (location_prefix + context.uuid)[:36]
    encounter_generator = encounter_factory()
    encounter_data = encounter_generator()
    encounter_data["patient_record_uuid"] = context.patient["record"]["uuid"]
    encounter_data["patient_uuid"] = context.patient["uuid"]
    encounter_data["dh_product_uuid"] = context.patient["dh_products"][0]["uuid"]
    encounter_data["location_uuid"] = location_uuid
    encounter_data.pop("epr_encounter_id")
    encounter = context.encounters_client.create_encounter(encounter_data).json()

    logger.debug("the encounter is (%s) %s" % (encounter["uuid"], encounter))

    context.encounter = encounter
    context.clues.append(("has an open encounter", encounter))


@then(
    "there are {num_patients} patients registered against {ward_prefix} in the ward list"
)
def check_ward_contains_specified_patients(
    context: Context, num_patients: str, ward_prefix: str
) -> None:
    ward_uuid = (ward_prefix + context.uuid)[:36]

    wards: List[Dict] = send_bff_client.get_ward_list().json()

    assert any(
        w.get("uuid") == ward_uuid and w.get("patients") == int(num_patients)
        for w in wards
    )
