class LambdaHandlerError(Exception):
    status_code: int = 500
    add_extra: bool = False
