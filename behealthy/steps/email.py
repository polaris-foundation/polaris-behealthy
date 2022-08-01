import email
import imaplib
from datetime import date, datetime, timedelta
from typing import List

from behave import then, when
from behave.runner import Context
from requests import Response
from she_http_clients.users import UsersApiClient
from she_logging import logger

from behealthy.utils.assertions import assert_stops_raising

GMAIL_USERNAME = "testsensyne@gmail.com"
GMAIL_PASSWORD = "sdfw87erftygeygr"


@when("a new clinician is created")
def create_new_clinician(context: Context) -> None:
    bh_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S")
    context.clinician_email = f"testsensyne+bh{bh_identifier}@gmail.com"
    clinician_details = {
        "email_address": context.clinician_email,
        "first_name": f"BeHealthy{bh_identifier}",
        "last_name": "BeHealthy",
        "job_title": "Doctor",
        "groups": ["SEND Clinician"],
        "locations": [],
        "phone_number": "",
        "nhs_smartcard_number": "",
        "send_entry_identifier": bh_identifier,
        "products": [{"opened_date": date.today().isoformat(), "product_name": "SEND"}],
    }
    client: UsersApiClient = context.users_client
    response: Response = client.create_clinician(
        clinician_data=clinician_details, send_welcome_email=True
    )
    clinician = response.json()
    context.clinicians_cleanup.append(
        {"clinician_uuid": clinician["uuid"], "product_name": "SEND"}
    )
    context.clinician = clinician


@then("the clinician receives a welcome email")
def check_email_received(context: Context) -> None:
    def retry_check_email_received(email_address: str) -> None:
        # Log into mailbox.
        imap_datestr = (date.today() - timedelta(days=1)).strftime("%d-%b-%Y")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        mail.select("inbox")
        _, data = mail.search(None, f'since "{imap_datestr}"')
        email_ids = data[0].split()

        # Search for email sent to the right alias.
        logger.info(
            "Searching %d emails for 'to' field %s", len(email_ids), email_address
        )
        is_matched = False
        for email_id in email_ids:
            typ, data = mail.fetch(email_id, "(RFC822)")
            is_matched = _check_email_match(data, email_address)
            if is_matched:
                break

        assert is_matched is True

    assert_stops_raising(
        fn=retry_check_email_received,
        args=(context.clinician_email,),
        exception_type=AssertionError,
        timeout=30,
        interval=1,
        delay=5,
    )


def _check_email_match(data: List, email_address: str) -> bool:
    for response_part in data:
        if (
            isinstance(response_part, tuple)
            and email.message_from_bytes(response_part[1])["to"] == email_address
        ):
            return True
    return False
