import os
from enum import auto

from chatbot_cloud_util.util import AutoName
from yarl import URL

from .exceptions import UnknownProviderError
from .interface import JWTVerifierInterface
from .okta_verifier import OktaJWTVerifier

jwt_verifier = None


class TokenType(AutoName):
    refresh_token = auto()
    access_token = auto()
    id_token = auto()



def get_verifier(provider: str, jwt_verifier_kwargs: dict) -> JWTVerifierInterface:
    global jwt_verifier
    if jwt_verifier is not None:
        return jwt_verifier
    if provider == 'okta':
        jwt_verifier = OktaJWTVerifier(**jwt_verifier_kwargs)
        return jwt_verifier
    raise UnknownProviderError(f"Unknown provider: {provider}")