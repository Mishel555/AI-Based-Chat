from chatbot_cloud_util.auth_utils.session_repository.interface import UserSessionData
from chatbot_cloud_util.decorators import (
    handle_exceptions,
    jsonify_body,
    login_required,
    trace_event,
)


@trace_event
@jsonify_body
@handle_exceptions
@login_required
def lambda_handler(event: dict, context, claims: UserSessionData):
    return {
        "statusCode": 200,
        "body": {
            "name": claims["name"],
            'email': claims['email'],
            'given_name': claims['given_name'],
            'family_name': claims['family_name'],
            "preferred_username": claims["preferred_username"],
            "zoneinfo": claims["zoneinfo"],
            "email_verified": claims["email_verified"],
        }
    }