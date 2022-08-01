import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

from behave import given, register_type, then, use_step_matcher, when
from behave.runner import Context
from requests import Response
from she_logging import logger

from behealthy.clients import aggregator_api_client, gdm_bff_client
from behealthy.utils.assertions import assert_stops_raising


def parse_boolean(bool_as_str: str) -> bool:
    return {"true": True, "false": False}[bool_as_str.lower()]


use_step_matcher("cfparse")
register_type(str=str, float=float, bool=parse_boolean)


@given('I generate certain BG readings "{bgreadingsfile}"')
def post_bg_readings(context: Context, bgreadingsfile: str) -> None:
    syne_scenario_file: Path = Path("behealthy/fixtures/" + bgreadingsfile)
    bg_readings: List[Dict] = json.loads(syne_scenario_file.read_text())

    start_today: datetime = datetime.now(tz=timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    for reading in bg_readings:
        relative_time_seconds = int(reading["measured_timestamp"])
        converted_dt: datetime = start_today + timedelta(
            days=1, seconds=relative_time_seconds
        )
        reading["measured_timestamp"] = converted_dt.isoformat(timespec="milliseconds")

        gdm_bff_client.post_gdm_bg_readings(context.patient["uuid"], reading)


@when("I trigger SYNE processing")
def syne_processing(context: Context) -> None:
    response: Response = aggregator_api_client.process_syne_bg_readings()
    response.raise_for_status()
    assert (
        response.status_code == 204
    ), f"Unexpected response {response.status_code} for request ID {response.headers.get('X-Request-Id')}"


@when("I attempt SYNE processing when SYNE is disabled")
def syne_attempted_processing(context: Context) -> None:
    response: Response = aggregator_api_client.process_syne_bg_readings()
    context.syne_response = response


@then("I see No SYNE data produced")
def syne_no_data_produced(context: Context) -> None:
    # We expect 200 when SYNE is disabled and 204 when it is enabled
    assert (
        context.syne_response.status_code == 200
    ), f"Unexpected response {context.syne_response.status_code} for request ID {context.syne_response.headers.get('X-Request-Id')}"


@then(
    'I see the expected SYNE predictions "{syneprediction:str}" "{medsprediction:str}" '
    '"{predictionvalue:float}" "{imputed:bool}" "{imputedvalue:float}"'
)
def syne_prediction(
    context: Context,
    syneprediction: str,
    medsprediction: str,
    predictionvalue: float,
    imputed: bool,
    imputedvalue: float,
) -> None:
    logger.info("Checking SYNE prediction for patient %s", context.patient["uuid"])
    assert_stops_raising(
        fn=check_syne_predictions,
        args=(
            context,
            syneprediction,
            medsprediction,
            predictionvalue,
            imputed,
            imputedvalue,
        ),
        exception_type=AssertionError,
        timeout=100,
        interval=2,
        delay=15,
    )


def check_syne_predictions(
    context: Context,
    syneprediction: str,
    medsprediction: str,
    predictionvalue: float,
    imputed: bool,
    imputedvalue: float,
) -> None:
    patient_mrn: str = context.patient["hospital_number"]
    patient_response: Response = gdm_bff_client.search_patient(patient_mrn)
    assert patient_response.status_code == 200

    patient_data: Dict = patient_response.json()
    assert "syne_predict_meds" in patient_data[0]
    actual_prediction = patient_data[0]["syne_predict_meds"]
    logger.info(f"Expected SYNE prediction {syneprediction}, got {actual_prediction}")
    assert actual_prediction == syneprediction

    assert "prediction" in patient_data[0]
    assert patient_data[0]["prediction"] is not None
    assert "prediction" in patient_data[0]["prediction"]
    actual_medsprediction = patient_data[0]["prediction"]["prediction"]
    logger.info(
        f"Expected meds prediction {medsprediction}, got {actual_medsprediction}"
    )
    assert actual_medsprediction == medsprediction

    # Verify Prediction Value
    assert "prediction_value" in patient_data[0]["prediction"]
    actual_predictionvalue = patient_data[0]["prediction"]["prediction_value"]
    logger.info(
        f"Expected prediction value {predictionvalue}, got {actual_predictionvalue}"
    )
    assert actual_predictionvalue == predictionvalue

    # Verify max_post_breakfast_bg_reading values
    assert "computed_features" in patient_data[0]["prediction"]
    actual_imputedvalue = patient_data[0]["prediction"]["computed_features"][
        "max_post_breakfast_bg_reading"
    ]["value"]
    logger.info(
        f"Expected max_post_breakfast_bg_reading imputed value {imputedvalue}, got {actual_imputedvalue}"
    )
    assert actual_imputedvalue == imputedvalue

    actual_imputed = patient_data[0]["prediction"]["computed_features"][
        "max_post_breakfast_bg_reading"
    ]["imputed"]
    logger.info(
        f"Expected max_post_breakfast_bg_reading imputed {imputed}, got {actual_imputed}"
    )
    assert actual_imputed == imputed


@then("I see No SYNE predictions")
def no_syne_prediction(context: Context) -> None:
    patient_mrn: str = context.patient["hospital_number"]
    patient_response: Response = gdm_bff_client.search_patient(patient_mrn)
    assert patient_response.status_code == 200

    patient_data: Dict = patient_response.json()
    assert patient_data[0]["syne_predict_meds"] == "NO_ACTION"

    assert "prediction" in patient_data[0]
    assert patient_data[0]["prediction"] is None
