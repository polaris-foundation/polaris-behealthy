import random
import re
import time
import uuid
from datetime import datetime
from operator import itemgetter
from typing import Dict, List, Optional

from behave import step, then, use_step_matcher, when
from behave.runner import Context
from requests.exceptions import HTTPError
from she_data_generation.observation import observation_set_factory
from she_data_generation.patient import nhs_number as generate_nhs_number
from she_data_generation.person import first_name, last_name
from she_data_generation.time import date_of_birth
from she_logging import logger

from behealthy.clients import send_bff_client
from behealthy.utils import hl7
from behealthy.utils.assertions import assert_stops_raising

PATIENT_INFORMATION_FIELDS = ["dob", "first_name", "last_name"]

use_step_matcher("re")


def generate_hl7_message(
    context: Context,
    adt_type: str,
    epr_encounter_id: str,
    discharged: bool = False,
    msg_ctrl_id: Optional[str] = None,
    include_message_segments: Optional[List] = None,
) -> str:
    _msg_ctrl_id: str = msg_ctrl_id or context.msg_ctrl_id

    if discharged:
        return hl7.generate_b64_message(
            adt_type=adt_type,
            ctrl_id=_msg_ctrl_id,
            mrn=context.mrn,
            nhs_number=context.nhs_number,
            location=context.hl7_location,
            epr_encounter_id=epr_encounter_id,
            dob=context.dob,
            first_name=context.first_name,
            last_name=context.last_name,
            discharge_datetime=datetime.now().strftime("%Y%m%d%H%M%S"),
        )

    return hl7.generate_b64_message(
        adt_type=adt_type,
        ctrl_id=_msg_ctrl_id,
        mrn=context.mrn,
        nhs_number=context.nhs_number,
        location=context.hl7_location,
        epr_encounter_id=epr_encounter_id,
        dob=context.dob,
        first_name=context.first_name,
        last_name=context.last_name,
        include_message_segments=include_message_segments,
    )


@when("I receive a valid ADT-A01 message")
def hl7_adt_a01(context: Context) -> None:
    _generate_patient_details(context)
    hl7_message = generate_hl7_message(context, "A01", context.epr_encounter_id)
    logger.info("Sending A01 message for EPR encounter ID %s", context.epr_encounter_id)
    response = context.connector_client.send_h17_message(hl7_message)
    sent_msg = response.json()
    logger.info("A01 message request ID: %s", response.headers.get("X-Request-Id"))
    context.message_uuid = sent_msg["uuid"]


@when("I receive a valid ADT-A01 message with non-latin1 characters")
def hl7_adt_a01_utf8(context: Context) -> None:
    _generate_patient_details(context)
    context.first_name = "Bén"
    context.last_name = "Var Hälsosam 건강 быть здоровым 健康 Vertu Heilbrigður"
    hl7_message = generate_hl7_message(context, "A01", context.epr_encounter_id)
    logger.info("Sending A01 message for EPR encounter ID %s", context.epr_encounter_id)
    response = context.connector_client.send_h17_message(hl7_message)
    sent_msg = response.json()
    logger.debug("A01 message request ID: %s", response.headers.get("X-Request-Id"))
    context.message_uuid = sent_msg["uuid"]


@when("I receive a valid ADT-A23 message")
def hl7_adt_a23(context: Context) -> None:
    _generate_patient_details(context)
    time.sleep(1)  # wait for potential earlier messages to process
    hl7_message = generate_hl7_message(context, "A23", context.epr_encounter_id)
    logger.info("Sending A23 message for EPR encounter ID %s", context.epr_encounter_id)
    response = context.connector_client.send_h17_message(hl7_message)
    sent_msg = response.json()
    logger.debug("A23 message request ID: %s", response.headers.get("X-Request-Id"))
    context.message_uuid = sent_msg["uuid"]


@step(
    "I receive a valid ADT-A01 message about a (?P<encounter>new|first|second|existing) encounter"
)
def hl7_adt_a01_new(context: Context, encounter: str) -> None:
    try:
        context.old_epr_id = context.epr_encounter_id
    except AttributeError:
        ...
    _generate_patient_details(context)
    encounter_id = str(uuid.uuid4())
    time.sleep(1)  # wait for potential earlier messages to process
    if encounter == "first":
        context.first_encounter = encounter_id
    elif encounter == "second":
        context.second_encounter = encounter_id
    elif encounter == "existing":
        encounter_id = context.epr_encounter_id

    hl7_message = generate_hl7_message(context, "A01", encounter_id)
    logger.info(
        "Sending A01 message for (%s) encounter ID %s",
        encounter,
        encounter_id,
    )
    response = context.connector_client.send_h17_message(hl7_message)
    sent_msg = response.json()
    logger.debug("A01 message request ID: %s", response.headers.get("X-Request-Id"))
    context.message_uuid = sent_msg["uuid"]


@step(
    "I receive a valid ADT-A03 for (?P<encounter>new|first|second|existing) encounter"
)
def hl7_adt_a03(context: Context, encounter: str) -> None:
    _generate_patient_details(context)
    time.sleep(1)  # wait for potential earlier messages to process
    if encounter == "first":
        context.epr_encounter_id = context.first_encounter
    elif encounter == "second":
        context.epr_encounter_id = context.second_encounter
    elif encounter == "new":
        context.epr_encounter_id = str(uuid.uuid4())

    hl7_message = generate_hl7_message(context, "A03", context.epr_encounter_id, True)
    logger.info(
        "Sending A03 message for EPR encounter (%s) ID %s",
        encounter,
        context.epr_encounter_id,
    )
    response = context.connector_client.send_h17_message(hl7_message)
    sent_msg = response.json()
    logger.debug("A03 message request ID: %s", response.headers.get("X-Request-Id"))
    context.message_uuid = sent_msg["uuid"]


@when("I receive a valid ADT-A02 message")
def hl7_adt_a02(context: Context) -> None:
    _generate_patient_details(context)
    context.ward = context.new_location["ods_code"]
    context.hl7_location = context.new_location["ods_code"]
    time.sleep(1)  # wait for potential earlier messages to process
    hl7_message = generate_hl7_message(context, "A02", context.epr_encounter_id)
    logger.info("Sending A02 message for EPR encounter ID %s", context.epr_encounter_id)
    response = context.connector_client.send_h17_message(hl7_message)
    sent_msg = response.json()
    logger.debug("A02 message request ID: %s", response.headers.get("X-Request-Id"))
    context.message_uuid = sent_msg["uuid"]


@when("I receive a valid ADT-A13 message")
def hl7_adt_a13(context: Context) -> None:
    _generate_patient_details(context)
    time.sleep(1)  # wait for potential earlier messages to process
    hl7_message = generate_hl7_message(context, "A13", context.epr_encounter_id)
    logger.info("Sending A13 message for EPR encounter ID %s", context.epr_encounter_id)
    response = context.connector_client.send_h17_message(hl7_message)
    sent_msg = response.json()
    logger.debug("A13 message request ID: %s", response.headers.get("X-Request-Id"))
    context.message_uuid = sent_msg["uuid"]


@when("I receive a valid ADT-(?P<adt_type>A04|A08|A28|A31).* message")
def hl7_adt_a04_08_28_31(context: Context, adt_type: str) -> None:
    _generate_patient_details(context)
    context.dob = date_of_birth(min_age=16).replace("-", "")
    context.first_name = first_name()
    context.last_name = last_name()
    hl7_message = generate_hl7_message(context, adt_type, context.epr_encounter_id)
    logger.info(
        "Sending %s message for EPR encounter ID %s", adt_type, context.epr_encounter_id
    )
    response = context.connector_client.send_h17_message(hl7_message)
    sent_msg = response.json()
    logger.debug(
        "%s message request ID: %s", adt_type, response.headers.get("X-Request-Id")
    )
    context.message_uuid = sent_msg["uuid"]


@when("I receive an ADT-(?P<adt_type>A\d\d) message with missing (?P<segment_name>\w+)")
def hl7_adt_a08_31_with_missing_segment(
    context: Context, adt_type: str, segment_name: str
) -> None:
    _generate_patient_details(context)
    context.patient_before_update = dict(context.patient)
    context.dob = date_of_birth(min_age=16).replace("-", "")
    context.first_name = first_name()
    context.last_name = last_name()
    segments = [
        segment for segment in hl7.DEFAULT_MESSAGE_SEGMENTS if segment != segment_name
    ]
    hl7_message = generate_hl7_message(
        context, adt_type, context.epr_encounter_id, False, str(uuid.uuid4()), segments
    )
    logger.info(
        "Sending %s message with missing %s for EPR encounter ID %s",
        adt_type,
        segment_name,
        context.epr_encounter_id,
    )
    try:
        response = context.connector_client.send_h17_message(hl7_message).json()
    except HTTPError as e:
        # messages with some missing segments get rejected straight away
        assert e.response.status_code == 400
        logger.debug("message rejected with HTTP 400")
    finally:
        # others result with AE
        context.message_uuid = response["uuid"]
        logger.debug("response uuid: %s", context.message_uuid)
        time.sleep(1)


@when("I take an observation set for the encounter")
def take_an_obs_set(context: Context) -> None:
    def _internal_check(context: Context) -> None:
        encounter_list: List[Dict] = context.encounters_client.find_encounter(
            epr_encounter_id=context.epr_encounter_id
        ).json()
        observation_set_generator = observation_set_factory(observation_probability=1)
        observation_set_data = observation_set_generator()
        assert len(encounter_list) > 0
        observation_set_data["encounter_id"] = encounter_list[0]["uuid"]

        observation_set: Dict = send_bff_client.create_send_observation_set(
            observation_set_data
        ).json()
        logger.info(
            "Posted obs set '%s' to encounter '%s'",
            observation_set["uuid"],
            observation_set_data["encounter_id"],
        )
        assert observation_set["encounter_id"] == encounter_list[0]["uuid"]
        context.observation_set_uuid = observation_set["uuid"]

    assert_stops_raising(
        fn=_internal_check, args=(context,), exception_type=AssertionError, timeout=25
    )


@then("the existing location is used")
def check_existing_location_is_used(context: Context) -> None:
    def get_location(context: Context) -> None:
        location = context.locations_client.get_location_by_ods_code(
            context.ward
        ).json()
        assert len(location) == 1
        logger.error(
            "Expected %s, got %s", context.location["uuid"], list(location.keys())[0]
        )
        assert list(location.keys())[0] == context.location["uuid"]

    assert_stops_raising(
        fn=get_location, args=(context,), exception_type=AssertionError
    )
    context.location_uuid = context.location["uuid"]


@then("the existing patient record is not updated")
def assert_existing_patient_is_not_updated(context: Context) -> None:
    patient_list = context.services_client.find_patient(
        product_name="SEND", identifier_type="MRN", identifier=context.mrn
    ).json()
    assert len(patient_list) == 1
    assert patient_list[0]["uuid"] == context.patient_before_update["uuid"]
    for field_name in PATIENT_INFORMATION_FIELDS:
        expected_value = patient_list[0][field_name]

        logger.info(
            "field: %s expected: %s actual %s",
            field_name,
            expected_value,
            context.patient_before_update[field_name],
        )
        assert expected_value == context.patient_before_update[field_name]


@then("the existing patient record is updated")
def check_existing_patient_is_used(context: Context) -> None:
    def get_patient(context: Context) -> None:
        patient_list = context.services_client.find_patient(
            product_name="SEND", identifier_type="MRN", identifier=context.mrn
        ).json()
        context.patients_cleanup.append(
            {
                "patient_uuid": patient_list[0]["uuid"],
                "product_uuid": patient_list[0]["dh_products"][0]["uuid"],
                "product_name": "SEND",
            }
        )
        assert len(patient_list) == 1
        assert patient_list[0]["uuid"] == context.patient["uuid"]
        for field_name in PATIENT_INFORMATION_FIELDS:
            expected_value = patient_list[0][field_name]
            if field_name == "dob":
                expected_value = expected_value.replace("-", "")  # handle HL7 date
            assert expected_value == getattr(context, field_name)

    assert_stops_raising(fn=get_patient, args=(context,))


@then("the encounter has the expected location history")
def check_encounter_location_history(context: Context) -> None:
    def retry_check_encounter_location_history(context: Context) -> None:
        encounter_list: List[Dict] = context.encounters_client.find_encounter(
            epr_encounter_id=context.epr_encounter_id
        ).json()
        assert len(encounter_list) == 1
        assert encounter_list[0]["uuid"] == context.encounter["uuid"]
        assert len(encounter_list[0]["location_history"])
        assert (
            encounter_list[0]["location_history"][0]["location_uuid"]
            == context.location["uuid"]
        )

    assert_stops_raising(fn=retry_check_encounter_location_history, args=(context,))


@then("the existing encounter is updated")
def check_existing_encounter_is_used(context: Context) -> None:
    def get_encounter(context: Context) -> None:
        encounter_list: List[Dict] = context.encounters_client.find_encounter(
            epr_encounter_id=context.epr_encounter_id
        ).json()
        assert len(encounter_list) == 1
        assert encounter_list[0]["uuid"] == context.encounter["uuid"]

    assert_stops_raising(fn=get_encounter, args=(context,))


@then("the encounter (?P<status>is.*) marked as discharged")
def check_encounter_is_discharged(context: Context, status: str) -> None:
    def retry_check_encounter_is_discharged(context: Context) -> None:
        logger.debug("Finding encounter ID %s", context.epr_encounter_id)
        encounter_list: List[Dict] = context.encounters_client.find_encounter(
            epr_encounter_id=context.epr_encounter_id
        ).json()
        logger.debug("Encounter list %s", encounter_list)
        assert len(encounter_list) == 1
        assert encounter_list[0]["uuid"] == context.encounter["uuid"]

        if status == "is":
            assert encounter_list[0]["discharged_at"] is not None
        elif status == "is not":
            assert encounter_list[0]["discharged_at"] is None

    assert_stops_raising(fn=retry_check_encounter_is_discharged, args=(context,))


@then("a new patient record is created")
def check_patient_record_is_created(context: Context) -> None:
    logger.debug("searching for patient with MRN: %s", context.mrn)

    def get_patient(context: Context) -> None:
        patient_list: List[Dict] = context.services_client.find_patient(
            product_name="SEND", identifier_type="MRN", identifier=context.mrn
        ).json()
        context.patients_cleanup.append(
            {
                "patient_uuid": patient_list[0]["uuid"],
                "product_uuid": patient_list[0]["dh_products"][0]["uuid"],
                "product_name": "SEND",
            }
        )
        assert len(patient_list) == 1

    assert_stops_raising(fn=get_patient, args=(context,))


@then("a new encounter is created")
def check_encounter_record_is_created(context: Context) -> None:
    def get_encounter(context: Context) -> None:
        encounter_list: List[Dict] = context.encounters_client.find_encounter(
            context.epr_encounter_id
        ).json()
        assert len(encounter_list) == 1
        context.new_encounter = encounter_list[0]

    assert_stops_raising(fn=get_encounter, args=(context,), timeout=25)


@then("a new location is created")
def check_location_record_is_created(context: Context) -> None:
    def get_location(context: Context) -> Dict[str, Dict]:
        location: Dict[str, Dict] = context.locations_client.get_location_by_ods_code(
            context.ward
        ).json()
        assert len(location) == 1
        return location

    location = assert_stops_raising(
        fn=get_location, args=(context,), exception_type=AssertionError
    )
    context.location_uuid = list(location.keys())[0]
    context.locations_cleanup.append(context.location_uuid)


@step("a new encounter is created alongside the old one")
def check_new_encounter_record_created(context: Context) -> None:
    def get_encounters(context: Context) -> None:
        encounter_list: List[Dict] = context.encounters_client.find_encounter(
            context.old_epr_id
        ).json()
        new_encounter_list: List[Dict] = context.encounters_client.find_encounter(
            context.epr_encounter_id
        ).json()
        assert len(encounter_list) == 1
        assert len(new_encounter_list) == 1

    assert_stops_raising(fn=get_encounters, args=(context,), timeout=25)


@then("the new encounter has a score system of (?P<score_system>\w*)")
def check_new_encounter_record_created_with_score_system(
    context: Context, score_system: str
) -> None:
    assert context.new_encounter["score_system"] == score_system


@then("the patient (?P<appears>.+) on the ward list for their location")
def check_patient_is_on_ward(context: Context, appears: str) -> None:
    def retry_check_patient_is_on_ward(context: Context, appears: str) -> None:
        logger.debug("check patient on ward location: %s", context.location_uuid)
        ward_list: Dict = send_bff_client.search_location_for_encounters(
            context.location_uuid
        ).json()
        logger.debug("Ward list: %s", ward_list)
        patient_record = {}
        for patient in ward_list["results"]:
            if patient.get("hospital_number") == context.mrn:
                patient_record = patient
                break

        if appears == "appears":
            assert patient_record.get("hospital_number") == context.mrn
        elif appears == "does not appear":
            assert patient_record == {}

    assert_stops_raising(
        fn=retry_check_patient_is_on_ward, args=(context, appears), timeout=25
    )


@then("the patient appears on the ward list for their new location")
def check_patient_is_on_new_ward(context: Context) -> None:
    def retry_check_patient_is_on_new_ward(context: Context) -> None:
        ward_list: Dict = send_bff_client.search_location_for_encounters(
            context.new_location["uuid"]
        ).json()
        patient_record = {}
        for patient in ward_list["results"]:
            if patient.get("hospital_number") == context.mrn:
                patient_record = patient
                break

        assert patient_record.get("hospital_number") == context.mrn

    assert_stops_raising(
        fn=retry_check_patient_is_on_new_ward, args=(context,), timeout=25
    )


@then("the patient and (?P<status>\w+) encounter can be found via search")
def check_patient_searchable(context: Context, status: str) -> None:
    ward_list: Dict = send_bff_client.search_patient_encounters(mrn=context.mrn).json()
    patient_record = {}
    for patient in ward_list["results"]:
        if patient.get("hospital_number") == context.mrn:
            patient_record = patient
            break

    assert patient_record.get("hospital_number") == context.mrn

    if status == "admitted":
        assert patient_record.get("discharged") is False
        assert patient_record.get("discharged_at") is None
    elif status == "discharged":
        assert patient_record.get("discharged") is True
        assert patient_record.get("discharged_at") is not None


@step("an ACK (?P<ack_status>A[A|E|R]) message is sent back to Connector API")
def check_ack_message(context: Context, ack_status: str) -> None:
    message: Dict = context.connector_client.get_h17_message(
        context.message_uuid
    ).json()
    assert "ack_status" in message
    logger.debug("ack_status: %s", message["ack_status"])
    assert message["ack_status"] == ack_status


@then("a new cancelled encounter is created")
def check_a_cancelled_encounter_record_is_created(context: Context) -> None:
    def get_encounter(context: Context) -> None:
        logger.debug("Finding encounter ID %s", context.epr_encounter_id)
        encounter_list: List[Dict] = context.encounters_client.find_encounter(
            epr_encounter_id=context.epr_encounter_id,
            show_deleted=True,
            show_children=True,
        ).json()
        logger.debug("Encounters: %s", encounter_list)
        assert len(encounter_list) == 1
        assert encounter_list[0]["deleted_at"] is not None

    assert_stops_raising(fn=get_encounter, args=(context,), interval=2, timeout=25)


@then("new cancelled and open encounters are created")
def check_new_cancelled_and_open_encounter_record_are_created(context: Context) -> None:
    def get_encounter(context: Context) -> None:
        encounter_list: List[Dict] = context.encounters_client.find_encounter(
            epr_encounter_id=context.epr_encounter_id,
            show_deleted=True,
            show_children=True,
        ).json()
        logger.info("Finding encounter ID %s", context.epr_encounter_id)
        logger.info("Encounters returned %s", encounter_list)
        assert len(encounter_list) == 2
        sorted_encounters = sorted(encounter_list, key=itemgetter("created"))
        assert sorted_encounters[0]["deleted_at"] is not None
        assert sorted_encounters[1]["deleted_at"] is None
        context.old_encounter_id = sorted_encounters[0]["uuid"]
        context.open_encounter_id = sorted_encounters[1]["uuid"]

    assert_stops_raising(fn=get_encounter, args=(context,), interval=2, timeout=25)


@then("the observation set is marked sent in Connector API")
def observations_sent_by_connector(context: Context) -> None:
    def get_hl7_msg(context: Context) -> None:
        mrn = context.patient["hospital_number"]
        hl7_msg_list: List[Dict] = context.connector_client.get_h17_message_by_mrn(
            identifier=mrn
        ).json()
        assert len(hl7_msg_list) == 1
        assert hl7_msg_list[0]["is_processed"] is True

        if "OBX|1|ST|ScoringSystem||NEWS2" in hl7_msg_list[0]["content"]:
            regex = r"(OBX|3|NM|TotalScore)([0-9\|cC]*)(\|0-4\|)"
            match = re.search(regex, hl7_msg_list[0]["content"], re.DOTALL)
            assert match and match.group(3) == "|0-4|"

        elif "OBX|1|ST|ScoringSystem||MEOWS" in hl7_msg_list[0]["content"]:
            regex = r"(OBX|3|NM|TotalScore)([0-9\|cC]*)(\|0\|)"
            match = re.search(regex, hl7_msg_list[0]["content"], re.DOTALL)
            assert match and match.group(3) == "|0|"

    assert_stops_raising(fn=get_hl7_msg, args=(context,), interval=2, timeout=25)


def _generate_patient_details(context: Context) -> None:
    context.msg_ctrl_id = str(uuid.uuid4())
    try:
        mrn = context.patient["hospital_number"]
        nhs_number = context.patient["nhs_number"]
    except AttributeError:
        mrn = str(random.randint(1, 999999999999)).zfill(12)
        nhs_number = generate_nhs_number()
    try:
        epr_encounter_id = context.epr_encounter_id
    except AttributeError:
        epr_encounter_id = str(uuid.uuid4())
        context.epr_encounter_id = epr_encounter_id
    try:
        ward = context.location["ods_code"]
        location = context.location["ods_code"]
    except AttributeError:
        ward = f"be-Healthy Ward {str(random.randint(1,1000))}"
        location = f"{ward}^Room {str(random.randint(1,1000))}^Bed {str(random.randint(1,1000))}"
    context.mrn = mrn
    context.nhs_number = nhs_number
    context.epr_encounter_id = epr_encounter_id
    context.ward = ward
    context.hl7_location = location

    for data in PATIENT_INFORMATION_FIELDS:
        if not hasattr(context, data):
            setattr(
                context,
                data,
                getattr(context, "patient", {}).get(data),
            )
        if data == "dob" and context.dob is not None:
            context.dob = context.dob.replace("-", "")  # handle HL7 date


@step("the (?P<encounter>new|first|second) encounter is (?P<status>open|discharged)")
def the_new_encounter_is_open(context: Context, encounter: str, status: str) -> None:
    def get_encounters(context: Context) -> None:
        if encounter == "first":
            encounter_id = context.first_encounter
        elif encounter == "second":
            encounter_id = context.second_encounter
        else:
            encounter_id = context.epr_encounter_id

        logger.info("Finding encounter (%s): %s", encounter, encounter_id)
        encounter_list: List[Dict] = context.encounters_client.find_encounter(
            encounter_id
        ).json()
        logger.info("Encounter returned: %s", encounter_id)

        assert len(encounter_list) == 1
        if status == "open":
            assert encounter_list[0]["discharged_at"] is None
        else:
            assert encounter_list[0]["discharged_at"] is not None

    assert_stops_raising(fn=get_encounters, args=(context,), timeout=25)
