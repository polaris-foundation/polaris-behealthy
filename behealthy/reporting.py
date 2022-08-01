import subprocess
from typing import List, Optional

from behave.runner import Context
from environs import Env
from reportportal_behave.behave_integration_service import BehaveIntegrationService

from behealthy import config

REPORT_PORTAL_ENDPOINT: Optional[str] = Env().str("REPORT_PORTAL_ENDPOINT", None)
REPORT_PORTAL_PROJECT: Optional[str] = Env().str("REPORT_PORTAL_PROJECT", None)
REPORT_PORTAL_TOKEN: Optional[str] = Env().str("REPORT_PORTAL_TOKEN", None)


def init_report_portal(context: Context) -> None:
    tags: str = ", ".join([tag for tags in context.config.tags.ands for tag in tags])
    rp_enable: bool = context.config.userdata.getbool("rp_enable", False)
    step_based: bool = context.config.userdata.getbool("step_based", True)
    add_screenshot: bool = context.config.userdata.getbool("add_screenshot", False)
    context.behave_integration_service = BehaveIntegrationService(
        rp_endpoint=REPORT_PORTAL_ENDPOINT,
        rp_project=REPORT_PORTAL_PROJECT,
        rp_token=REPORT_PORTAL_TOKEN,
        rp_launch_name=f"Be-Healthy",
        rp_launch_description=f"Be-Healthy end-to-end platform tests",
        rp_enable=rp_enable,
        step_based=step_based,
        add_screenshot=add_screenshot,
        verify_ssl=True,
    )
    attributes = {"environment": config.ENVIRONMENT, "release": _get_git_tag()}
    context.launch_id = context.behave_integration_service.launch_service(
        attributes=attributes, tags=tags
    )


def _get_git_tag() -> str:
    stdout: str = subprocess.run(
        ["git", "tag", "--sort=creatordate"],
        capture_output=True,
        text=True,
    ).stdout
    last_line: List[str] = stdout.splitlines()[-1:]
    return last_line[0].replace("v", "")
