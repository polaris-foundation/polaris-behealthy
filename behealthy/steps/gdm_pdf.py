import hashlib

from behave import given, then, when
from behave.runner import Context
from requests import Response

from behealthy.clients import gdm_bff_client


@given("a GDM PDF {exists_or_not} for that patient")
def generate_gdm_pdf(context: Context, exists_or_not: str) -> None:
    if exists_or_not == "does not exist":
        # No-op
        return
    patient_uuid: str = context.patient["uuid"]
    gdm_bff_response: Response = gdm_bff_client.get_gdm_pdf(patient_uuid)
    assert gdm_bff_response.status_code == 200
    pdf: bytes = gdm_bff_response.content
    assert isinstance(pdf, bytes)
    hasher = hashlib.md5()
    hasher.update(pdf)
    context.existing_pdf_hash = hasher.hexdigest()


@when("I request the PDF")
def request_pdf(context: Context) -> None:
    response: Response = gdm_bff_client.get_gdm_pdf(context.patient["uuid"])
    assert (
        response.status_code == 200
    ), f"Expected 200 but got {response.status_code}, request ID {response.headers.get('X-Request-Id')}"
    context.pdf_response = response


@then("I receive the PDF")
def check_pdf(context: Context) -> None:
    assert context.pdf_response.headers["Content-Type"] == "application/pdf"
    assert isinstance(context.pdf_response.content, bytes)
    assert len(context.pdf_response.content) > 0


@then("the PDF has not been regenerated")
def check_pdf_not_changed(context: Context) -> None:
    new_pdf: bytes = context.pdf_response.content
    hasher = hashlib.md5()
    hasher.update(new_pdf)
    assert hasher.hexdigest() == context.existing_pdf_hash
