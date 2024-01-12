import dataclasses
import typing
import uuid
from inspect import signature

import aws_cdk as cdk
import ulid

API_CORS_HEADERS_NON_PROD = {
    'allow_headers': [
        'Content-Type', 'X-Amz-Date', 'Authorization',
        'X-Api-Key', 'X-Amz-Security-Token', 'X-Amz-User-Agent', 'Cookie',
    ],
    'allow_methods': [
        'OPTIONS', 'GET', 'PUT', 'POST', 'HEAD',
    ],
    'allow_origins': ['http://localhost:8080'],
    'allow_credentials': True,
}


@dataclasses.dataclass
class EnvironmentContext:
    environment: str
    unique_env_key: str
    jwt_secret_key_full_arn: str
    openai_secret_key_full_arn: str

    # auth envs
    auth0_url: str
    auth0_client_id: str

    # domain envs
    certificate_arn: str
    hosted_zone_id: str
    zone_name: str

    # defaults with possibility to be overwritten via cdk context
    leap_url: str = "https://leap.fsp-pi.com/"
    log_apigw_event: str = ''
    access_key_audience: str = 'api://default'
    api_base_url: typing.Optional[str] = None
    api_redirect_extra_path: str = ''
    auth0_login_callback: str = 'auth/login_callback'
    success_login_redirect_path: str = ''
    redis_host: typing.Optional[str] = None
    redis_port: typing.Optional[int] = None

    bucket_name_chatbot_requests_context: str = 'chatbot-requests-context'
    bucket_name_chatbot_chat_history: str = 'chat-history'
    bucket_name_static_website: str = 'static-website'
    bucket_object_chatbot_request_prefix_tpl: str = '{year}-{month}/{day}/{chat_id}/{id}.json'
    bucket_object_chatbot_history_prefix_tpl: str = '{year}-{month}/{day}/{chat_id}/'

    ecr_name_vector_store_faissdb: str = 'flagship-chatbot-conda-env-py3.9'
    ecr_name_lambda_api_start_chat: str = 'flagship-chatbot-conda-env-py3.9'
    ecr_name_lambda_api_login_lambda: str = 'flagship-chatbot-conda-env-py3.9'
    ecr_name_lambda_api_login_callback_lambda: str = 'flagship-chatbot-conda-env-py3.9'
    ecr_name_lambda_api_user_handler_lambda: str = 'flagship-chatbot-conda-env-py3.9'
    ecr_name_lambda_api_logout_lambda: str = 'flagship-chatbot-conda-env-py3.9'
    ecr_name_lambda_ws_api: str = 'flagship-chatbot-conda-env-py3.9'
    ecr_name_lambda_ws_api_human_input: str = 'flagship-chatbot-conda-env-py3.9'
    ecr_name_lambda_ws_api_custom_assertion: str = 'flagship-chatbot-conda-env-py3.9'
    ecr_name_lambda_ws_api_task_token: str = 'flagship-chatbot-conda-env-py3.9'
    ecr_name_lambda_step_obfuscator: str = 'flagship-chatbot-conda-env-py3.9'
    ecr_name_lambda_step_statement_creator: str = 'flagship-chatbot-conda-env-py3.9'
    ecr_name_lambda_step_assertions_creator_task_token_notificator: str = 'flagship-chatbot-conda-env-py3.9'
    ecr_name_lambda_step_assertions_creator: str = 'flagship-chatbot-conda-env-py3.9'
    ecr_name_lambda_step_evidence_creator_task_token_notificator: str = 'flagship-chatbot-conda-env-py3.9'
    ecr_name_lambda_step_evidence_creator: str = 'flagship-chatbot-conda-env-py3.9'

    image_tag_prefix_vector_store_faissdb: str = 'aws-lambda-vector-store-faissdb'
    image_tag_prefix_lambda_api_start_chat: str = 'aws-lambda-api-start-chat'
    image_tag_prefix_lambda_api_login: str = 'aws-lambda-api-login'
    image_tag_prefix_lambda_api_login_callback: str = 'aws-lambda-api-login-callback'
    image_tag_prefix_lambda_api_user: str = 'aws-lambda-api-user'
    image_tag_prefix_lambda_api_logout: str = 'aws-lambda-api-logout'
    image_tag_prefix_lambda_ws_api: str = 'aws-lambda-api'
    image_tag_prefix_lambda_ws_api_human_input: str = 'aws-lambda-api-human-input'
    image_tag_prefix_lambda_ws_api_custom_assertion: str = 'aws-lambda-api-custom-assertion'
    image_tag_prefix_lambda_ws_api_task_token: str = 'aws-lambda-api-task-token'
    image_tag_prefix_lambda_step_obfuscator: str = 'aws-lambda-step-obfuscator'
    image_tag_prefix_lambda_step_statement_creator: str = 'aws-lambda-step-statement-creator'
    image_tag_prefix_lambda_step_assertions_creator_task_token_notificator: str = \
        'aws-lambda-step-task-token-notificator'
    image_tag_prefix_lambda_step_assertions_creator: str = 'aws-lambda-step-assertions-creator'
    image_tag_prefix_lambda_step_evidence_creator_task_token_notificator: str = 'aws-lambda-step-task-token-notificator'
    image_tag_prefix_lambda_step_evidence_creator: str = 'aws-lambda-step-evidence-creator'

    lambda_name_api_start_chat: str = 'api-start-chat'
    lambda_name_ws_api: str = 'ws-api'
    lambda_name_ws_api_human_input: str = 'ws-api-human-input'
    lambda_name_ws_api_custom_assertion: str = 'ws-api-custom-assertion'
    lambda_name_ws_api_task_token: str = 'ws-api-task-token'
    lambda_name_step_obfuscator: str = 'step-obfuscator'
    lambda_name_step_statement_creator: str = 'step-statement-creator'
    lambda_name_step_assertions_creator_task_token_notificator: str = 'step-assertions-creator-task-token-notificator'
    lambda_name_step_assertions_creator: str = 'step-assertions-creator'
    lambda_name_step_evidence_creator_task_token_notificator: str = 'step-evidence-creator-task-token-notificator'
    lambda_name_step_evidence_creator: str = 'step-evidence-creator'

    lambda_name_step_obfuscator_extra_env_vars: typing.Tuple[tuple] = ()
    lambda_name_step_statement_creator_extra_env_vars: typing.Tuple[tuple] = ()
    lambda_name_step_assertions_creator_task_token_notificator_extra_env_vars: typing.Tuple[tuple] = (
        ('existing_state_type', 'statement'),
    )
    lambda_name_step_assertions_creator_extra_env_vars: typing.Tuple[tuple] = ()
    lambda_name_step_evidence_creator_task_token_notificator_extra_env_vars: typing.Tuple[tuple] = (
        ('existing_state_type', 'assertion'),
    )
    lambda_name_step_evidence_creator_extra_env_vars: typing.Tuple[tuple] = ()

    llm_name: str = 'chat_openai'
    non_dev_environments: typing.Tuple[str, str] = ('staging', 'production')
    production_environments: typing.Tuple[str] = ('production',)

    vector_store_desired_tasks_count: int = 1
    vector_store_max_tasks_count: int = 1
    vector_store_vpc_max_azs: int = 2
    vector_store_cpu_units: int = 2048
    vector_store_memory_limit_mib: int = 4096

    assertions_workflow_state_machine_name: str = 'assertions-to-evidence-sm'
    human_input_workflow_state_machine_name: str = 'human-input-to-evidence-sm'

    ws_connections_table_name_ddb: str = 'ws-connections'

    def name(self, n: str):
        return f'{self.environment}-{n}'

    @property
    def unique_env_suffix(self):
        return ulid.from_uuid(uuid.uuid5(uuid.NAMESPACE_DNS, f'{self.environment}.{self.unique_env_key}')).str.lower()

    @property
    def is_prod(self):
        return self.environment in self.production_environments

    @property
    def is_dev(self):
        return not self.is_non_dev

    @property
    def is_non_dev(self):
        return self.environment in self.non_dev_environments

    @classmethod
    def from_kwargs(cls, **kwargs):
        cls_fields = {field for field in signature(cls).parameters}
        ret = cls(**{name: val for name, val in kwargs.items() if name in cls_fields})
        return ret


def print_hr(text, hr_above=True, hr_below=True):
    if hr_above:
        print('-' * 80)
    print(text)
    if hr_below:
        print('-' * 80)


def load_environment_context(app: cdk.App) -> EnvironmentContext:
    try:
        env_name = app.node.get_context('env')
    except Exception as e:
        print_hr(f'Got exception during env loading: {str(e)}')
        exit(1)

    try:
        env_context = app.node.get_context(env_name)
    except Exception:
        print_hr(f'Specify environment [{env_name}] configuration through the permanent context in cdk.json')
        exit(1)

    return EnvironmentContext.from_kwargs(**env_context)
