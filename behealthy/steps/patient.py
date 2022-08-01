import io
from datetime import date, timedelta
from typing import Callable, Dict

import draymed
from behave import given, then
from behave.runner import Context
from environs import Env
from PyPDF2 import PdfFileReader
from requests import HTTPError
from she_data_generation.patient import Sex, patient_factory
from she_http_clients.pdf import PdfApiClient
from she_logging import logger

from behealthy.utils.assertions import assert_keeps_raising, assert_stops_raising


@given("a SEND patient exists")
def create_send_patient(context: Context) -> None:
    location_uuid: str = context.location["uuid"]
    patient_generator: Callable = patient_factory(
        locations=[location_uuid], product_name="SEND", patient_sex=Sex.ANY
    )
    patient_data: Dict = patient_generator()
    patient: Dict = context.services_client.create_patient(
        patient_data, product_name="SEND"
    ).json()

    logger.debug("the patient is %s" % patient)

    context.patient = patient
    context.patients_cleanup.append(
        {
            "patient_uuid": patient["uuid"],
            "product_uuid": patient["dh_products"][0]["uuid"],
            "product_name": "SEND",
        }
    )
    context.clues.append(("a SEND patient exists", patient))


@given("has no BCP PDF")
def assert_bcp_pdf_missing(context: Context) -> None:
    encounter_uuid: str = context.encounter["uuid"]
    client: PdfApiClient = context.pdf_client
    assert_keeps_raising(
        client.get_patient_pdf,
        kwargs={"encounter_uuid": encounter_uuid},
        exception_type=HTTPError,
        timeout=7,
        interval=2,
        delay=4,
    )


@then("the BCP PDF is generated")
def assert_patient_pdf_exists(context: Context) -> None:
    encounter_uuid: str = context.encounter["uuid"]
    client: PdfApiClient = context.pdf_client

    def try_and_get_pdf() -> None:
        raw_bytes: bytes = client.get_patient_pdf(encounter_uuid=encounter_uuid).content
        pdf_reader: PdfFileReader = PdfFileReader(io.BytesIO(raw_bytes))
        number_of_pages: int = pdf_reader.getNumPages()
        number_of_bytes: int = len(raw_bytes)
        logger.debug(
            f"received pdf: {number_of_pages} pages, {number_of_bytes} bytes"  # noqa
        )
        context.populated_pdf = {"pages": number_of_pages, "bytes": number_of_bytes}
        assert number_of_pages > 0

    # This one might take a while.
    assert_stops_raising(try_and_get_pdf, timeout=60, interval=2, delay=4)


@given("a GDM patient exists")
def create_gdm_patient(context: Context) -> None:
    patient_generator: Callable = patient_factory(
        locations=["static_location_uuid_L2"], product_name="GDM", patient_sex=Sex.ANY
    )
    patient_data: Dict = patient_generator()
    patient_data["phone_number"] = Env().str("SMS_TO_NUMBER", "07777777777")
    patient_data["dh_products"][0]["accessibility_discussed"] = True
    patient_data["dh_products"][0]["accessibility_discussed_date"] = str(date.today())
    patient_data["dh_products"][0]["accessibility_discussed_with"] = "system"
    # To avoid sending the "You can download" message
    patient_data["allowed_to_text"] = False
    date_now_iso8601: str = str(date.today())
    date_future_iso8601: str = str(date.today() + timedelta(days=30))
    patient_data["record"] = {
        # We need this stuff for the GDM PDF and to be able to close the record.
        "pregnancies": [
            {
                "estimated_delivery_date": date_future_iso8601,
                "height_at_booking_in_mm": 2000,
                "weight_at_booking_in_g": 2000,
                "length_of_postnatal_stay_in_days": 5,
                "induced": False,
            }
        ],
        "diagnoses": [
            {
                "sct_code": draymed.codes.code_from_name(
                    name="gdm", category="diabetes_type"
                ),
                "management_plan": {
                    "start_date": date_now_iso8601,
                    "end_date": date_future_iso8601,
                    "sct_code": draymed.codes.code_from_name(
                        name="dietAndExercise", category="management_type"
                    ),
                    "doses": [],
                },
                "readings_plan": {
                    "sct_code": "33747003",
                    "start_date": date_now_iso8601,
                    "end_date": date_future_iso8601,
                    "days_per_week_to_take_readings": 4,
                    "readings_per_day": 4,
                },
                "diagnosed": date_now_iso8601,
                "diagnosis_tool": [
                    draymed.codes.code_from_name(
                        name="nice20080hr", category="diagnosis_tool"
                    )
                ],
                "risk_factors": [
                    draymed.codes.code_from_name(
                        name="previousGdm", category="risk_factor"
                    )
                ],
            }
        ],
    }

    response: Dict = context.services_client.create_patient(
        patient_data=patient_data,
        product_name="GDM",
    ).json()
    assert "uuid" in response
    context.patient = response
    context.patients_cleanup.append(
        {
            "patient_uuid": response["uuid"],
            "product_uuid": response["dh_products"][0]["uuid"],
            "product_name": "GDM",
        }
    )
