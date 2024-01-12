import requests
from chatbot_cloud_util.auth_utils.session_repository import get_redis_repository
from jose import ExpiredSignatureError, jwk, jwt
from yarl import URL

from .exceptions import JWTVerifierError
from .interface import JWTVerifierInterface


class OktaJWTVerifier(JWTVerifierInterface):
    HMAC_REDIS_KEY = "jkw_hmac_data"

    def __init__(self, auth0_url: str, audience: str = 'api://default', env: str = "default"):
        self._auth0_url = auth0_url
        self._audience = audience
        self._env = env

    def _construct_jwks_uri(self):
        return URL(self._auth0_url).with_path(f"/oauth2/{self._env}/v1/keys")

    def _get_hmac_key(self):
        repository = get_redis_repository()
        hmac = repository.get_hmac(self.HMAC_REDIS_KEY)
        if hmac is None:
            hmac = requests.get(self._construct_jwks_uri()).json()
            hmac = hmac["keys"][0]
            repository.store_hmac(self.HMAC_REDIS_KEY, hmac)
        return jwk.construct(hmac)

    def verify_access_token(
        self,
        token: str,
        claims_to_verify=("iss", "aud", "exp"),
    ):
        hmac_key = self._get_hmac_key()
        try:
            return jwt.decode(
                token,
                hmac_key,
                algorithms=("RS256",),
                audience=self._audience,
                options={
                    "verify_exp": True,
                    "verify_aud": True,
                    "verify_iss": True,
                    "verify_signature": True,
                    "verify_at_hash": True,
                    "verify_authorized_party": True,
                    "leeway": 0,
                    "claims": claims_to_verify,
                },
            )
        except ExpiredSignatureError:
            raise
        except Exception as e:
            raise JWTVerifierError(e) from e
