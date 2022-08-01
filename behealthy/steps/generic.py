from behave import given
from behave.runner import Context


@given("I have a valid jwt")
def get_jwt_for_user(context: Context) -> None:
    # TODO create jwt for context.clinician... but for now:
    context.jwt = context.users_client.jwt
