from chatbot_cloud_util.common_exceptions import LambdaHandlerError


class AuthError(LambdaHandlerError):
    ...


class CookieNotFoundError(AuthError):
    status_code = 403


class SessionNotFoundError(AuthError):
    status_code = 403


class CookieDecodeError(AuthError):
    status_code = 403


class NoStageVariableFoundError(AuthError):
    ...
    
    
class UnauthorizedError(AuthError):
    status_code = 403