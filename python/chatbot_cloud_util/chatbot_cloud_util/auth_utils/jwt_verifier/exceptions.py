from chatbot_cloud_util.auth_utils.exceptions import AuthError


class JWTVerifierError(AuthError):
    ...
    

class UnknownProviderError(JWTVerifierError):
    pass