from typing import Dict, List, Optional

import requests
from behave import given, then, when
from behave.runner import Context
from requests import Response
from requests.exceptions import HTTPError
from she_http_clients.observations import ObservationsApiClient
from she_logging import logger

from behealthy.clients import send_bff_client
from behealthy.utils import obs_sets
from behealthy.utils.assertions import assert_stops_raising

# not scored in News2
IGNORED_OBSERVATIONS = ["diastolic_blood_pressure", "nurse_concern"]


@when("I submit a NEWS2 Observation Set")
def send_news_observation_set(context: Context) -> None:
    def send_news_observation_set_build() -> None:
        try:
            observation_set_data: Dict = obs_sets.generate_obs_set(score_system="news2")
            if not hasattr(context, "encounter"):
                encounters: List[Dict] = send_bff_client.get_encounters_by_patient_id(
                    context.patient["uuid"]
                ).json()
                context.clues.append(("Encounters", encounters))
                context.encounter = encounters[0]
            observation_set_data["encounter_id"] = context.encounter["uuid"]
            response: Response = send_bff_client.create_send_observation_set(
                observation_set_data
            )
            response.raise_for_status()
            observation_set: Dict = response.json()
        except HTTPError:
            logger.warning(
                'failed to create observation set with data: "%s"', observation_set_data
            )
            raise

        logger.info(
            "Successfully created NEWS2 obs set with UUID %s", observation_set["uuid"]
        )
        context.clues.append(("I submit a NEWS2 Observation Set", observation_set))

    assert_stops_raising(fn=send_news_observation_set_build, exception_type=IndexError)


@when("I submit a MEOWS Observation Set")
def send_meows_observation_set(context: Context) -> None:
    observation_set_data: Dict = obs_sets.generate_obs_set(score_system="meows")
    observation_set_data["encounter_id"] = context.encounter["uuid"]

    nurse_concern_idx: Optional[int] = None
    measured_time: Optional[str] = None
    for idx, obs in enumerate(observation_set_data.get("observations", [])):
        if not measured_time:
            measured_time = obs.get("measured_time")
        if obs.get("observation_type") == "nurse_concern":
            nurse_concern_idx = idx
            break

    if not nurse_concern_idx:
        nurse_concern_idx = len(observation_set_data["observations"])
        observation_set_data["observations"].append({})

    observation_set_data["observations"][nurse_concern_idx] = {
        "measured_time": measured_time,
        "observation_string": "Looks unwell, Low urine output (< 25ml / hr)",
        "observation_type": "nurse_concern",
        "observation_unit": "",
        "patient_refused": False,
    }

    try:
        response: Response = send_bff_client.create_send_observation_set(
            observation_set_data
        )
        response.raise_for_status()
        observation_set: Dict = response.json()
    except HTTPError:
        logger.warning(
            'failed to create observation set with data: "%s"', observation_set_data
        )
        raise

    logger.info(
        "Successfully created MEOWS obs set with UUID %s", observation_set["uuid"]
    )
    context.observation_set = observation_set
    context.clues.append(("I submit a MEOWS Observation Set", observation_set))


@given("I have no existing observation sets")
def check_no_existing_observation_sets(context: Context) -> None:
    client: ObservationsApiClient = context.observations_client
    encounter: Dict = context.encounter
    observation_set: Optional[Dict]
    try:
        response: Response = client.get_latest_observation_set_by_encounter_id(
            encounter_id=encounter["uuid"]
        )
        response.raise_for_status()
        observation_set = response.json()
    except HTTPError as exc:
        response = exc.response
        if response.status_code == 404:
            observation_set = None
        else:
            raise

    assert not observation_set


@then("I have an Observation Set with a Score")
def check_latest_observation_set_is_scored(context: Context) -> None:
    client: ObservationsApiClient = context.observations_client
    encounter: Dict = context.encounter

    def check_exists_and_has_score() -> None:
        observation_set: Optional[Dict]
        try:
            response: Response = client.get_latest_observation_set_by_encounter_id(
                encounter_id=encounter["uuid"]
            )
            response.raise_for_status()
            observation_set = response.json()
        except requests.exceptions.RequestException:
            observation_set = None

        assert observation_set

        observations = observation_set["observations"]
        for observation in observations:
            if observation["observation_type"] in IGNORED_OBSERVATIONS:
                continue

            context.most_recent_assertion = (
                f"{observation['score_value']} is not None for observation: "
                f"{observation}"
            )
            assert observation["score_value"] is not None

        context.most_recent_assertion = f"{observation_set['score_value']} is not None"
        assert observation_set["score_value"] is not None
        context.most_recent_assertion = f"{observation_set['score_value']} >= 0"
        assert observation_set["score_value"] >= 0

    assert_stops_raising(fn=check_exists_and_has_score, exception_type=AssertionError)


@then("the observations are connected to the discharged encounter")
def observations_connected_discharged_encounter(context: Context) -> None:
    encounter = context.discharge_encounter
    response: Response = send_bff_client.get_send_observation_sets_by_encounter_id(
        encounter_id=encounter["uuid"]
    )
    response.raise_for_status()
    observation_sets: List[Dict] = response.json()
    context.clues.append(
        ("The observations are connected to the discharged encounter", observation_sets)
    )
    assert observation_sets[0].get("score_value") is not None
