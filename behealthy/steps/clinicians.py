from typing import Callable, Dict, Optional

from behave import given, use_step_matcher
from behave.runner import Context
from she_data_generation.clinician import Sex, clinician_factory
from she_data_generation.location import Location, location_factory
from she_http_clients.users import UsersApiClient

use_step_matcher("re")


@given("I have a working location")
def create_send_working_location(context: Context) -> None:
    create_working_location(context, product_name="SEND")


@given(
    "I have a working location with a default score system of (?P<score_system>meows|news2|NULL)"
)
def create_send_working_location_default_score_system(
    context: Context, score_system: str
) -> None:
    parsed_score_system: Optional[str] = (
        None if score_system == "NULL" else score_system
    )
    location_generator: Callable = location_factory(
        product_name="SEND", loc_type=Location.WARD
    )
    location_data: Dict = location_generator()
    location_data["score_system_default"] = parsed_score_system
    location: Dict = context.locations_client.create_location(location_data).json()
    context.location = location
    context.clues.append(
        (
            f"I have a working location with a default score system of {score_system}",
            location["uuid"],
        )
    )
    context.locations_cleanup.append(location["uuid"])


@given("I have a working location with (?P<product_name>SEND Entry|SEND|GDM)")
def create_working_location(context: Context, product_name: str) -> None:
    location_generator: Callable = location_factory(
        product_name=product_name, loc_type=Location.WARD
    )
    location_data: Dict = location_generator()
    location: Dict = context.locations_client.create_location(location_data).json()
    context.location = location
    context.clues.append(("I have a working location", location["uuid"]))
    context.locations_cleanup.append(location["uuid"])


@given("I have another location to transfer to")
def create_another_working_location(context: Context) -> None:
    location_generator: Callable = location_factory(
        product_name="SEND", loc_type=Location.WARD
    )
    location_data: Dict = location_generator()
    location: Dict = context.locations_client.create_location(location_data).json()
    context.new_location = location
    context.clues.append(("I have another location to transfer to", location["uuid"]))
    context.locations_cleanup.append(location["uuid"])


@given("I am a Clinician using (?P<full_product_name>SEND Entry|SEND|GDM)")
def create_clinician_and_get_jwt(context: Context, full_product_name: str) -> None:
    product_name = full_product_name if full_product_name != "SEND Entry" else "SEND"
    location_uuid = context.location["uuid"]
    clinician_generator: Callable = clinician_factory(
        groups=[f"{full_product_name} Clinician"],
        product_name=product_name,
        locations=[location_uuid],
        clinician_sex=Sex.ANY,
    )
    clinician_data: Dict = clinician_generator()
    users_client: UsersApiClient = context.users_client
    clinician: Dict = users_client.create_clinician(
        clinician_data=clinician_data, send_welcome_email=False
    ).json()
    context.clinicians_cleanup.append(
        {
            "clinician_uuid": clinician["uuid"],
            "product_name": product_name,
        }
    )
    context.user = clinician
    context.clues.append((f"I am a Clinician using {full_product_name}", clinician))
