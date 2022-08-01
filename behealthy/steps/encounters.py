import uuid
from typing import Callable, Dict, List

from behave import given, then
from behave.runner import Context
from she_data_generation.encounter import encounter_factory
from she_logging import logger

from behealthy.clients import send_bff_client
from behealthy.utils.assertions import assert_stops_raising


@given("has an open encounter")
def create_encounter(context: Context) -> None:
    encounter_generator: Callable = encounter_factory()
    encounter_data: Dict = encounter_generator()
    encounter_data["patient_record_uuid"] = context.patient["record"]["uuid"]
    encounter_data["patient_uuid"] = context.patient["uuid"]
    encounter_data["dh_product_uuid"] = context.patient["dh_products"][0]["uuid"]
    encounter_data["location_uuid"] = context.location["uuid"]
    encounter_data.pop("epr_encounter_id")
    encounter: Dict = context.encounters_client.create_encounter(encounter_data).json()

    logger.debug("the encounter is (%s) %s" % (encounter["uuid"], encounter))

    context.encounter = encounter
    context.clues.append(("has an open encounter", encounter))


@given("an EPR encounter exists")
def create_epr_encounter(context: Context) -> None:
    encounter_generator: Callable = encounter_factory()
    encounter_data: Dict = encounter_generator()
    encounter_data["patient_record_uuid"] = context.patient["record"]["uuid"]
    encounter_data["patient_uuid"] = context.patient["uuid"]
    encounter_data["dh_product_uuid"] = context.patient["dh_products"][0]["uuid"]
    encounter_data["location_uuid"] = context.location["uuid"]
    try:
        encounter_data["epr_encounter_id"] = context.epr_encounter_id
    except AttributeError:
        encounter_data["epr_encounter_id"] = str(uuid.uuid4())
        context.epr_encounter_id = encounter_data["epr_encounter_id"]

    encounter: Dict = context.encounters_client.create_encounter(encounter_data).json()

    logger.debug("the encounter is (%s) %s" % (encounter["uuid"], encounter))

    context.encounter = encounter
    context.clues.append(("an EPR encounter exists", encounter))


@then("a discharged local encounter is created")
def discharged_encounter_created(context: Context) -> None:
    def get_encounter(context: Context) -> None:
        encounter_list: List[Dict] = send_bff_client.get_encounters_by_patient_id(
            patient_uuid=context.patient["uuid"],
        ).json()
        context.clues.append(("encounter_list", encounter_list))

        assert len(encounter_list) == 1

        assert encounter_list[0]["deleted_at"] is None
        assert encounter_list[0]["discharged_at"] is not None
        assert encounter_list[0]["epr_encounter_id"] is None
        context.discharge_encounter = encounter_list[0]

    assert_stops_raising(fn=get_encounter, args=(context,), interval=2, timeout=25)
