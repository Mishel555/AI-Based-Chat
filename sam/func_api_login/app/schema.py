INPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "Input Schema",
    "description": "",
    "properties": {
        "body": {
            "type": "object",
            "properties": {
                "human_input": {
                    "type": "string",
                },
            },
            "required": [
                "human_input",
            ],
        },
        "requestContext": {
            "type": "object",
            "properties": {
                "stage": {
                    "type": "string",
                },
            },
            "required": [
                "stage",
            ],
        },
        "headers": {
            "type": "object",
            "properties": {
                "x-jwt-token": {
                    "type": "string",
                },
            },
            "required": [
                "x-jwt-token",
            ],
        },
        "stageVariables": {
            "type": "object",
            "properties": {
                "jwt_secret_key_name": {
                    "type": "string",
                    "title": "Name of the secrets manager secret key used to decode JWT tokens",
                },
                "workflow_state_machine_arn": {
                    "type": "string",
                    "title": "ARN of StepFunctions state machine to trigger",
                },
                "chatbot_requests_bucket": {
                    "type": "string",
                    "title": "Name of the bucket where processing results are stored",
                },
            },
            "required": [
                "jwt_secret_key_name",
                "workflow_state_machine_arn",
                "chatbot_requests_bucket",
            ],
        },
    },
    "required": [
        "body",
        "requestContext",
        "headers",
        "stageVariables",
    ],
}

OUTPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "Output Schema",
    "description": "",
    "properties": {
        "statusCode": {
            "type": "integer",
            "title": "HTTP Status Code",
        },
        "body": {
            "type": "object",
            "title": "Payload body",
            "properties": {
                "request_id": {
                    "type": "string",
                    "minLength": 36,
                    "maxLength": 36,
                },
            },
        },
    },
    "required": [
        "statusCode",
        "body",
    ],
}
