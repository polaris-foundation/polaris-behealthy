from typing import Any, Callable, Dict

from she_data_generation.observation import observation_set_factory


def generate_obs_set(score_system: str) -> Dict[str, Any]:
    """
    Because we remove refused observations, occasionally we generate an obs set with no
    observations. So we keep trying until we get an obs set with observations.
    """
    while True:
        obs_set_data: Dict = _generate(score_system)
        if len(obs_set_data["observations"]) > 0:
            return obs_set_data


def _generate(score_system: str) -> Dict[str, Any]:
    observation_set_generator: Callable = observation_set_factory(
        observation_probability=1, score_system=score_system
    )
    observation_set_data: Dict = observation_set_generator()

    # remove randomness that is embedded within `observation_set_factory`
    observation_set_data["observations"] = [
        o for o in observation_set_data["observations"] if _has_value(o)
    ]
    return observation_set_data


def _has_value(observation: Dict) -> bool:
    return observation["patient_refused"] is False and (
        "observation_value" in observation or "observation_string" in observation
    )
