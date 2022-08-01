import datetime
import traceback
from typing import Dict, List

from behave.model import Feature, Scenario, Step
from behave.runner import Context
from she_http_clients.connector import ConnectorApiClient
from she_http_clients.encounters import EncountersApiClient
from she_http_clients.locations import LocationsApiClient
from she_http_clients.observations import ObservationsApiClient
from she_http_clients.pdf import PdfApiClient
from she_http_clients.services import ServicesApiClient
from she_http_clients.users import UsersApiClient
from she_logging import logger

from behealthy import config
from behealthy.reporting import init_report_portal


def before_all(context: Context) -> None:
    logger.debug("configuring behealthy")
    context.failures = []
    context.most_recent_assertion = ""
    context.connector_client = ConnectorApiClient(base_url=config.URL_BASE)
    context.pdf_client = PdfApiClient(base_url=config.URL_BASE)
    context.services_client = ServicesApiClient(base_url=config.URL_BASE)
    context.users_client = UsersApiClient(base_url=config.URL_BASE)
    context.encounters_client = EncountersApiClient(base_url=config.URL_BASE)
    context.observations_client = ObservationsApiClient(base_url=config.URL_BASE)
    context.locations_client = LocationsApiClient(base_url=config.URL_BASE)
    init_report_portal(context)
    logger.debug("behealthy is configured")


def before_feature(context: Context, feature: Feature) -> None:
    context.feature_id = context.behave_integration_service.before_feature(feature)


def before_scenario(context: Context, scenario: Scenario) -> None:
    context.scenario_id = context.behave_integration_service.before_scenario(
        scenario, feature_id=context.feature_id
    )
    context.clues = []
    context.patients_cleanup = []
    context.locations_cleanup = []
    context.clinicians_cleanup = []
    context.most_recent_assertion = ""


def before_step(context: Context, step: Step) -> None:
    context.step_id = context.behave_integration_service.before_step(
        step, scenario_id=context.scenario_id
    )


def after_step(context: Context, step: Step) -> None:
    context.behave_integration_service.after_step(step, context.step_id)
    if step.status == "failed":
        if context.most_recent_assertion:
            logger.error("most recent assertion: %s", context.most_recent_assertion)

        stack = traceback.format_tb(step.exc_traceback)
        if stack:
            logger.error(stack)

    context.most_recent_assertion = ""


def after_scenario(context: Context, scenario: Scenario) -> None:
    context.behave_integration_service.after_scenario(scenario, context.scenario_id)
    if scenario.status == "failed":
        logger.warning('scenario failed: "%s"', scenario.name)
        context.failures.append(scenario.name)

        logger.info("showing all clues collected during scenario execution")
        for clue in context.clues:
            clue_name, data = clue
            logger.info(clue_name)
            logger.info(clue)

    logger.debug("cleaning up test data created during scenario execution")
    for patient in context.patients_cleanup:
        if patient["product_name"] == "GDM":
            context.add_cleanup(
                context.services_client.close_patient,
                patient_uuid=patient["patient_uuid"],
                product_id=patient["product_uuid"],
                closure_data={
                    "closed_date": (
                        datetime.datetime.now() - datetime.timedelta(days=1)
                    ).strftime("%Y-%m-%d"),
                    "closed_reason_other": "Be-healthy e2e tests teardown.",
                },
            )
        encounters: List[Dict] = context.encounters_client.get_encounters_for_patient(
            patient_id=patient["patient_uuid"]
        ).json()
        for encounter in encounters:
            context.add_cleanup(
                context.encounters_client.update_encounter,
                encounter_id=encounter["uuid"],
                encounter_data={
                    "discharged_at": str(datetime.datetime.now().isoformat())[:-3]
                    + "+00:00",
                    "deleted_at": str(datetime.datetime.now().isoformat())[:-3]
                    + "+00:00",
                },
            )
    for clinician in context.clinicians_cleanup:
        context.add_cleanup(
            context.users_client.update_clinician,
            clinician_uuid=clinician["clinician_uuid"],
            product_name=clinician["product_name"],
            clinician_data={"login_active": False},
        )
    for location_uuid in context.locations_cleanup:
        context.add_cleanup(
            context.locations_client.update_location,
            location_uuid=location_uuid,
            location_data={"active": False},
        )


def after_feature(context: Context, feature: Feature) -> None:
    context.behave_integration_service.after_feature(feature, context.feature_id)


def after_all(context: Context) -> None:
    context.behave_integration_service.after_all(context.launch_id)
