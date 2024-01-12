from chatbot_cloud_util.common_exceptions import LambdaHandlerError


class LogoutLambdaError(LambdaHandlerError):
    ...
    
    
class RevokeTokenError(LogoutLambdaError):
    status_code = 500
