from datetime import datetime
from typing import Dict, Optional

from behave import given, then, when
from behave.runner import Context
from requests import Response

from behealthy.clients import gdm_bff_client
from behealthy.utils.assertions import assert_stops_raising


@given("the patient has SMS enabled")
def update_patient_smsable(context: Context) -> None:
    patch_response = context.services_client.update_patient(
        patient_uuid=context.patient["uuid"],
        update_data={"allowed_to_text": True},
    )
    context.patient = patch_response.json()


@when("I send the patient a message")
def send_message(context: Context) -> None:
    message_details = {
        "sender": "static_clinician_gdm_standard_1",
        "sender_type": "clinician",
        "receiver": context.patient["uuid"],
        "receiver_type": "patient",
        "message_type": {"value": 0},  # DHOS-MESSAGES-GENERAL
        "content": "Message from behealthy at "
        + datetime.utcnow().isoformat(timespec="milliseconds"),
    }
    response = gdm_bff_client.create_message(message_details=message_details)
    context.message_send_response = response.json()


@then("Polaris attempts to send an SMS message using Twilio")
def check_sms_message_exists(context: Context) -> None:
    def retry_check_sms_message_exists() -> str:
        response: Response = gdm_bff_client.get_all_sms(
            receiver=context.patient["phone_number"], limit=5
        )
        response.raise_for_status()
        matching_sms: Optional[Dict] = next(
            (
                m
                for m in response.json()
                if m["content"].startswith(context.message_send_response["content"])
            ),
            None,
        )
        assert matching_sms is not None
        return matching_sms["uuid"]

    sms_uuid: str = assert_stops_raising(
        retry_check_sms_message_exists,
        exception_type=AssertionError,
        timeout=25,
        interval=1,
        delay=3,
    )
    context.sms_uuid = sms_uuid


@then("I see that the Twilio callback has succeeded")
def check_callback_succeeded(context: Context) -> None:
    sms_uuid: str = context.sms_uuid

    def retry_check_callback_succeeded() -> None:
        response: Response = gdm_bff_client.get_sms_by_uuid(sms_uuid=sms_uuid)
        response.raise_for_status()
        # Twilio should at least have sent the message.
        assert response.json()["status"] in [
            "sent",
            "delivered",
            "undelivered",
            "failed",
        ]

    assert_stops_raising(
        retry_check_callback_succeeded,
        exception_type=AssertionError,
        timeout=60,
        interval=5,
        delay=3,
    )
