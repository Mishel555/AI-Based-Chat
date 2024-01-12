import aws_cdk as cdk
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_route53 as route53

from cdk.common import API_CORS_HEADERS_NON_PROD

from .auth_api import AuthAPIStack
from .backend import BackendStack
from .base_infra.stack import BaseInfraStack


class CommonAPIStack(cdk.Stack):

    def __init__(
            self,
            scope: cdk.App,
            construct_id: str,
            base_infra_stack: BaseInfraStack,
            auth_api_stack: AuthAPIStack,
            backend_api_stack: BackendStack,
            **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        self._env_context = base_infra_stack.env_context
        self.api_stage_variables = {
            'jwt_secret_key_name': base_infra_stack.jwt_secret_key.secret_name,
            'openai_secret_key_name': base_infra_stack.openai_secret_key.secret_name,
            'assertions_workflow_state_machine_arn':
                backend_api_stack.assertions_workflow_state_machine.state_machine_arn,
            'human_input_workflow_state_machine_arn':
                backend_api_stack.human_input_workflow_state_machine.state_machine_arn,
            'chatbot_requests_bucket': base_infra_stack.request_context_bucket.bucket_name,
            'chatbot_chat_history_bucket': base_infra_stack.chat_history_bucket.bucket_name,
        }
        self._base_infra = base_infra_stack
        self._auth_infra = auth_api_stack
        self._backend_infra = backend_api_stack
        
        zone_name = self._env_context.zone_name
        hz_id = self._env_context.hosted_zone_id
        self.hosted_zone = route53.HostedZone.from_hosted_zone_attributes(
            self,
            self._env_context.name('hosted_zone'),
            hosted_zone_id=hz_id,
            zone_name=zone_name,
        )
        self.cert = acm.Certificate.from_certificate_arn(
            self,
            f'{self._env_context.environment}-cert',
            self._env_context.certificate_arn,
        )
        
        self.api = self.configure_api_gateway(self._env_context.name('common-api'))
        self.api_ws = backend_api_stack.api_ws

        
    def configure_api_gateway(self, gateway_name: str):
        stage = apigw.StageOptions(
            stage_name=self._env_context.environment,
            variables=self.api_stage_variables,
        )
        api = apigw.RestApi(
            self,
            gateway_name,
            rest_api_name=gateway_name,
            deploy_options=stage,
            binary_media_types=['*/*'],
            min_compression_size=cdk.Size.bytes(0),
        )

        domain_name_str = f'{self._env_context.environment}-chat' \
            if self._env_context.is_dev else self._env_context.environment
        self._set_domain_name(api, domain_name_str)
        self.configure_auth_lambdas(api)
        self.configure_backend_lambdas(api)
        self.configure_frontend(api)
        cdk.CfnOutput(self, f'{api.rest_api_name}-url', value=api.url)
        return api
    
    def _set_domain_name(self, api, domain_name_str: str):
        zone_name = self._env_context.zone_name
        hosted_zone = self.hosted_zone
        fqdn = zone_name if self._env_context.is_prod else f'{domain_name_str}.{zone_name}'
        custom_domain = api.add_domain_name(
            fqdn,
            domain_name=fqdn,
            certificate=self.cert
        )
        route53.CnameRecord(
            self,
            domain_name_str,
            record_name=domain_name_str,
            zone=hosted_zone,
            domain_name=custom_domain.node.default_child.attr_regional_domain_name,
            delete_existing=True,
            ttl=cdk.Duration.seconds(60),
        )
        return custom_domain

    def configure_backend_lambdas(self, api: apigw.RestApi):
        backend_stack = self._backend_infra
        validator = api.root.add_resource('validator')
        chat_session = validator.add_resource('chat_session')
        chat_session.add_method('POST', apigw.LambdaIntegration(backend_stack.api_start_chat_lambda))

        if not self._env_context.is_prod:
            chat_session.add_cors_preflight(**API_CORS_HEADERS_NON_PROD)

        return validator

    def configure_auth_lambdas(self, api: apigw.RestApi):
        auth_stack = self._auth_infra
        login_lambda = auth_stack.rest_api.api_login
        login_callback_lambda = auth_stack.rest_api.api_login_callback
        logout_lambda = auth_stack.rest_api.api_logout
        user_lambda = auth_stack.rest_api.api_user

        resource = api.root.add_resource('auth')

        login_api_resource = resource.add_resource("login")
        login_api_resource.add_method("GET", apigw.LambdaIntegration(login_lambda))

        login_callback_resource = resource.add_resource("login_callback")
        login_callback_resource.add_method(
            "GET", apigw.LambdaIntegration(login_callback_lambda)
        )

        logout_resource = resource.add_resource("logout")
        logout_resource.add_method("POST", apigw.LambdaIntegration(logout_lambda))
        
        user_resource = resource.add_resource("user")
        user_resource.add_method("GET", apigw.LambdaIntegration(user_lambda))

        if not self._env_context.is_prod:
            login_api_resource.add_cors_preflight(**API_CORS_HEADERS_NON_PROD)
            login_callback_resource.add_cors_preflight(**API_CORS_HEADERS_NON_PROD)
            logout_resource.add_cors_preflight(**API_CORS_HEADERS_NON_PROD)
            user_resource.add_cors_preflight(**API_CORS_HEADERS_NON_PROD)

        return resource

    def configure_frontend(self, api: apigw.RestApi):
        static_website_resource = api.root.add_resource('app')
        proxy = static_website_resource.add_proxy()
        proxy.add_method(
            'GET',
            integration=apigw.AwsIntegration(
                service='s3',
                integration_http_method='GET',
                path=self._base_infra.static_website_bucket.bucket_name + '/{proxy}',
                options=apigw.IntegrationOptions(
                    credentials_role=self._base_infra.static_website_bucket_role,
                    passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_MATCH,
                    request_parameters={
                        'integration.request.path.proxy': 'method.request.path.proxy'
                    },
                    integration_responses=[apigw.IntegrationResponse(status_code='200')]
                ),
            ),
            method_responses=[apigw.MethodResponse(status_code='200')],
            request_parameters={'method.request.path.proxy': True}
        )
        return static_website_resource
