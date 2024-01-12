class ValidatorError(Exception):
    status_code: int = 500


class NoAssertionsGenerated(ValidatorError):
    status_code: int = 400


class IncompleteDocumentsListFound(ValidatorError):
    status_code: int = 502


class NoRelevantDocumentsFound(ValidatorError):
    status_code: int = 400
