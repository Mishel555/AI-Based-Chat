from chatbot_cloud_util.common_exceptions import LambdaHandlerError


class LoginHandlerError(LambdaHandlerError):
    ...


class CookieNotFoundError(LoginHandlerError):
    status_code: int = 400


class NoEnoughParametersError(LoginHandlerError):
    status_code: int = 400


class TokenNotFoundError(LoginHandlerError):
    status_code: int = 403


class NoStageVariableFound(LoginHandlerError):
    status_code: int = 500


class AppStateDoesNotMatchError(LoginHandlerError):
    status_code = 400


class CodeError(LambdaHandlerError):
    status_code = 403
