from typing import Optional

import aws_cdk as cdk
import aws_cdk.aws_cloudwatch as cloudwatch
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks
from aws_cdk import aws_apigatewayv2 as apigw2
from aws_cdk import aws_apigatewayv2_alpha as apigw2_alpha
from aws_cdk import aws_ec2 as ec2
from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration

from cdk.base_infra import BaseInfraStack
from cdk.common import API_CORS_HEADERS_NON_PROD


class BackendStack(cdk.Stack):
    def __init__(
            self,
            scope: cdk.App,
            base_infra_stack: BaseInfraStack,
            construct_id: str,
            **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        self.env_context = base_infra_stack.env_context
        self.sha_ref = base_infra_stack.sha_ref
        self.jwt_secret_key = base_infra_stack.jwt_secret_key
        self.openai_secret_key = base_infra_stack.openai_secret_key

        # buckets
        self.request_context_bucket = base_infra_stack.request_context_bucket
        self.static_website_bucket = base_infra_stack.static_website_bucket
        self.chat_history_bucket = base_infra_stack.chat_history_bucket

        self.vpc = base_infra_stack.vpc.vpc
        self.lambdas_security_group = base_infra_stack.lambdas_sec_group
        self._common_envs = base_infra_stack.common_envs
        self._base_infra = base_infra_stack

        self.step_lambdas = self._configure_step_lambdas()
        self.api_lambdas = self._configure_api_lambdas()
        self.assertions_workflow_state_machine = self._step_functions_assertions_workflow_state_machine()
        self.human_input_workflow_state_machine = self._step_functions_human_input_workflow_state_machine()
        self.workflow_state_machines = (
            self.assertions_workflow_state_machine,
            self.human_input_workflow_state_machine,
        )

        self.api_stage_variables = {
            'jwt_secret_key_name': base_infra_stack.jwt_secret_key.secret_name,
            'openai_secret_key_name': base_infra_stack.openai_secret_key.secret_name,
            'assertions_workflow_state_machine_arn': self.assertions_workflow_state_machine.state_machine_arn,
            'human_input_workflow_state_machine_arn': self.human_input_workflow_state_machine.state_machine_arn,
            'chatbot_requests_bucket': base_infra_stack.request_context_bucket.bucket_name,
            'chatbot_chat_history_bucket': base_infra_stack.chat_history_bucket.bucket_name,
            "leap_url": self.env_context.leap_url,
        }
        self.api_ws = self.configure_websocket_api(self.env_context.name('ws-api'))
        # self.connections_table = self._dynamo_db()

        self._adjust_policies()
        self._state_machine_cloudwatch_dashboard()

    def _adjust_policies(self):
        for step_lambda in self.step_lambdas:
            self.openai_secret_key.grant_read(step_lambda)
            self.request_context_bucket.grant_read_write(step_lambda)
            self.chat_history_bucket.grant_read_write(step_lambda)
            self.api_ws.grant_manage_connections(step_lambda)

        for api_lambda in self.api_lambdas:
            self.jwt_secret_key.grant_read(api_lambda)
            self.request_context_bucket.grant_read_write(api_lambda)
            self.chat_history_bucket.grant_read_write(api_lambda)

        # self.connections_table.grant_read_write_data(self.ws_api_lambda)
        self.assertions_workflow_state_machine.grant_start_execution(self.ws_api_custom_assertion_lambda)
        self.human_input_workflow_state_machine.grant_start_execution(self.ws_api_human_input_lambda)

        for m in self.workflow_state_machines:
            m.grant_task_response(self.ws_api_task_token_lambda)

    def configure_websocket_api(self, gateway_name: str):
        api_ws = apigw2_alpha.WebSocketApi(
            self,
            gateway_name,
            api_name=gateway_name,
            connect_route_options=apigw2_alpha.WebSocketRouteOptions(
                integration=WebSocketLambdaIntegration('ConnectIntegration', self.ws_api_lambda)),
            disconnect_route_options=apigw2_alpha.WebSocketRouteOptions(
                integration=WebSocketLambdaIntegration('DisconnectIntegration', self.ws_api_lambda)),
            default_route_options=apigw2_alpha.WebSocketRouteOptions(
                integration=WebSocketLambdaIntegration('DefaultIntegration', self.ws_api_lambda)),
        )
        api_ws.add_route(
            'human_input',
            integration=WebSocketLambdaIntegration('human_input', self.ws_api_human_input_lambda),
            return_response=False,
        )
        api_ws.add_route(
            'custom_assertion',
            integration=WebSocketLambdaIntegration('custom_assertion', self.ws_api_custom_assertion_lambda),
            return_response=False,
        )
        api_ws.add_route(
            'task_token',
            integration=WebSocketLambdaIntegration('task_token', self.ws_api_task_token_lambda),
            return_response=False,
        )
        cfn_stage = apigw2.CfnStage(
            self,
            self.env_context.name('api-ws-stage'),
            api_id=api_ws.api_id,
            stage_name=self.env_context.environment,
            auto_deploy=True,
            stage_variables=self.api_stage_variables,
        )
        cdk.CfnOutput(self, f'{api_ws.web_socket_api_name}-url', value=api_ws.api_endpoint)

        ws_connections_arns = self.format_arn(
            service='execute-api',
            resource=api_ws.api_id,
            resource_name=f'{cfn_stage.stage_name}/POST/*',
        )

        # self._set_domain_name(api_ws, domain_name_str)
        cdk.CfnOutput(self, f'{api_ws.web_socket_api_name}-domain-name', value=api_ws.web_socket_api_name)
        cdk.CfnOutput(self, f'{api_ws.web_socket_api_name}-arn', value=ws_connections_arns)
        return api_ws

    def _configure_step_lambdas(self) -> list[lambda_.Function]:
        environment = {
            'POWERTOOLS_METRICS_NAMESPACE': self.env_context.environment,
            'chatbot_request_prefix_tpl': self.env_context.bucket_object_chatbot_request_prefix_tpl,
            'chatbot_chat_history_prefix_tpl': self.env_context.bucket_object_chatbot_history_prefix_tpl,
            'llm_name': self.env_context.llm_name,
            **self._common_envs,
        }
        obfuscator_lambda_name = self.env_context.lambda_name_step_obfuscator
        obfuscator_lambda_envs = {**environment}
        self.step_obfuscator_lambda = self._init_lambda(
            obfuscator_lambda_name,
            self.env_context.ecr_name_lambda_step_obfuscator,
            tag_prefix=self.env_context.image_tag_prefix_lambda_step_obfuscator,
            lambda_envs=obfuscator_lambda_envs,
            timeout=cdk.Duration.minutes(15)
        )
        statement_creator_lambda_name = self.env_context.lambda_name_step_statement_creator
        statement_creator_lambda_envs = {**environment}
        self.step_statement_creator_lambda = self._init_lambda(
            statement_creator_lambda_name,
            self.env_context.ecr_name_lambda_step_statement_creator,
            tag_prefix=self.env_context.image_tag_prefix_lambda_step_statement_creator,
            lambda_envs=statement_creator_lambda_envs,
            timeout=cdk.Duration.minutes(15),
        )
        assertion_creator_lambda_name = self.env_context.lambda_name_step_assertions_creator
        assertion_creator_lambda_envs = {**environment}
        self.step_assertions_creator_lambda = self._init_lambda(
            assertion_creator_lambda_name,
            self.env_context.ecr_name_lambda_step_assertions_creator,
            tag_prefix=self.env_context.image_tag_prefix_lambda_step_assertions_creator,
            lambda_envs=assertion_creator_lambda_envs,
            timeout=cdk.Duration.minutes(15),
        )
        evidence_creator_lambda_name = self.env_context.lambda_name_step_evidence_creator
        evidence_creator_lambda_envs = {**environment}
        self.step_evidence_creator_lambda = self._init_lambda(
            evidence_creator_lambda_name,
            self.env_context.ecr_name_lambda_step_evidence_creator,
            tag_prefix=self.env_context.image_tag_prefix_lambda_step_evidence_creator,
            lambda_envs=evidence_creator_lambda_envs,
            timeout=cdk.Duration.minutes(15),
        )
        step_assertions_creator_lambda_name = \
            self.env_context.lambda_name_step_assertions_creator_task_token_notificator
        step_assertions_creator_lambda_envs = {
            **environment,
            **(dict(
                self.env_context.lambda_name_step_assertions_creator_task_token_notificator_extra_env_vars)
               or {})
        }
        self.step_assertions_creator_task_token_notificator_lambda = self._init_lambda(
            step_assertions_creator_lambda_name,
            self.env_context.ecr_name_lambda_step_assertions_creator_task_token_notificator,
            tag_prefix=self.env_context.image_tag_prefix_lambda_step_assertions_creator_task_token_notificator,
            lambda_envs=step_assertions_creator_lambda_envs,
            timeout=cdk.Duration.minutes(15),
        )
        task_token_notificator_lambda_name = self.env_context.lambda_name_step_evidence_creator_task_token_notificator
        task_token_notificator_lambda_envs = {
            **environment,
            **(dict(
                self.env_context.lambda_name_step_evidence_creator_task_token_notificator_extra_env_vars)
               or {})
        }
        self.step_evidence_creator_task_token_notificator_lambda = self._init_lambda(
            task_token_notificator_lambda_name,
            self.env_context.ecr_name_lambda_step_evidence_creator_task_token_notificator,
            tag_prefix=self.env_context.image_tag_prefix_lambda_step_evidence_creator_task_token_notificator,
            lambda_envs=task_token_notificator_lambda_envs,
            timeout=cdk.Duration.minutes(15),
        )

        return [
            self.step_obfuscator_lambda,
            self.step_statement_creator_lambda,
            self.step_assertions_creator_task_token_notificator_lambda,
            self.step_assertions_creator_lambda,
            self.step_evidence_creator_task_token_notificator_lambda,
            self.step_evidence_creator_lambda,
        ]

    def _configure_api_lambdas(self):
        environment = {
            'POWERTOOLS_METRICS_NAMESPACE': self.env_context.environment,
            'chatbot_request_prefix_tpl': self.env_context.bucket_object_chatbot_request_prefix_tpl,
            'chatbot_chat_history_prefix_tpl': self.env_context.bucket_object_chatbot_history_prefix_tpl,
            'llm_name': self.env_context.llm_name,
            **self._common_envs,
        }
        if not self.env_context.is_prod:
            for k, v in API_CORS_HEADERS_NON_PROD.items():
                environment.setdefault(k, ','.join(v) if type(v) in (list, tuple) else str(v))

        start_chat_lambda_name = self.env_context.lambda_name_api_start_chat
        start_chat_lambda_envs = {**environment}
        self.api_start_chat_lambda = self._init_lambda(
            start_chat_lambda_name,
            self.env_context.ecr_name_lambda_api_start_chat,
            tag_prefix=self.env_context.image_tag_prefix_lambda_api_start_chat,
            lambda_envs=start_chat_lambda_envs,
        )

        ws_api_lambda_name = self.env_context.lambda_name_ws_api
        ws_api_lambda_envs = {**environment}
        self.ws_api_lambda = self._init_lambda(
            ws_api_lambda_name,
            self.env_context.ecr_name_lambda_ws_api,
            tag_prefix=self.env_context.image_tag_prefix_lambda_ws_api,
            lambda_envs=ws_api_lambda_envs,
        )

        human_input_lambda_name = self.env_context.lambda_name_ws_api_human_input
        human_input_lambda_envs = {**environment}
        self.ws_api_human_input_lambda = self._init_lambda(
            human_input_lambda_name,
            self.env_context.ecr_name_lambda_ws_api_human_input,
            tag_prefix=self.env_context.image_tag_prefix_lambda_ws_api_human_input,
            lambda_envs=human_input_lambda_envs
        )

        custom_assertion_lambda_name = self.env_context.lambda_name_ws_api_custom_assertion
        custom_assertion_lambda_envs = {**environment}
        self.ws_api_custom_assertion_lambda = self._init_lambda(
            custom_assertion_lambda_name,
            self.env_context.ecr_name_lambda_ws_api_custom_assertion,
            tag_prefix=self.env_context.image_tag_prefix_lambda_ws_api_custom_assertion,
            lambda_envs=custom_assertion_lambda_envs,
        )

        ws_api_task_token_lambda_name = self.env_context.lambda_name_ws_api_task_token
        ws_api_task_token_lambda_envs = {**environment}
        self.ws_api_task_token_lambda = self._init_lambda(
            ws_api_task_token_lambda_name,
            self.env_context.ecr_name_lambda_ws_api_task_token,
            tag_prefix=self.env_context.image_tag_prefix_lambda_ws_api_task_token,
            lambda_envs=ws_api_task_token_lambda_envs,
        )

        return [
            self.api_start_chat_lambda,
            self.ws_api_lambda,
            self.ws_api_human_input_lambda,
            self.ws_api_custom_assertion_lambda,
            self.ws_api_task_token_lambda,
        ]

    def _init_lambda(
            self,
            lambda_name: str,
            repository_name: str,
            lambda_envs: dict,
            tag_prefix: Optional[str] = None,
            timeout: cdk.Duration = cdk.Duration.seconds(29),
    ) -> lambda_.Function:
        ecr_repo = ecr.Repository.from_repository_name(
            self,
            f'{lambda_name}-ecr-repo',
            repository_name,
        )
        cloudwatch.Metric(
            namespace=self.env_context.environment,
            metric_name=self.env_context.name(lambda_name)
        )
        lambda_envs.update({'POWERTOOLS_SERVICE_NAME': self.env_context.name(lambda_name)})
        return lambda_.Function(
            self,
            lambda_name,
            function_name=self.env_context.name(lambda_name),
            runtime=lambda_.Runtime.FROM_IMAGE,
            code=lambda_.Code.from_ecr_image(
                ecr_repo,
                tag_or_digest=f'{tag_prefix}-{self.sha_ref}' if tag_prefix else self.sha_ref,
            ),
            handler=lambda_.Handler.FROM_IMAGE,
            environment=lambda_envs,
            memory_size=512,
            timeout=timeout,
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[self.lambdas_security_group],
        )

    def _dynamo_db(self) -> dynamodb.Table:
        return dynamodb.Table(
            self,
            'ws-connections-table',
            table_name=self.env_context.name(self.env_context.ws_connections_table_name_ddb),
            partition_key=dynamodb.Attribute(
                name='connection_id',
                type=dynamodb.AttributeType.STRING
            ),
        )

    def _step_functions_assertions_workflow_state_machine(self):
        fail_step = sfn.Fail(self, f'{self.env_context.assertions_workflow_state_machine_name}-fail')
        succeed_step = sfn.Succeed(self, f'{self.env_context.assertions_workflow_state_machine_name}-succeeded')

        evidence_task_token_step = tasks.LambdaInvoke(
            self,
            f'{self.env_context.assertions_workflow_state_machine_name}-evidence-creator-task-token',
            lambda_function=self.step_evidence_creator_task_token_notificator_lambda,
            integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            payload=sfn.TaskInput.from_object({
                'task_token': sfn.JsonPath.task_token,
                'body': sfn.JsonPath.string_at('$')
            }),
        )
        evidence_creator_step = tasks.LambdaInvoke(
            self,
            f'{self.env_context.assertions_workflow_state_machine_name}-evidence-creator',
            lambda_function=self.step_evidence_creator_lambda,
            output_path='$.Payload',
        )
        evidence_creator_map_step = sfn.Map(
            self,
            f'{self.env_context.assertions_workflow_state_machine_name}-evidence-creator-map',
            items_path='$',
        ).iterator(
            sfn.Choice(self, 'Is custom assertion?')
            .when(sfn.Condition.is_present('$.requestContext.routeKey').and_(
                sfn.Condition.string_equals('$.requestContext.routeKey', 'custom_assertion')
            ), evidence_creator_step)
            .otherwise(evidence_task_token_step.next(evidence_creator_step))
        )
        evidence_creator_map_statuses_step = sfn.Pass(
            self,
            f'{self.env_context.assertions_workflow_state_machine_name}-evidence-creator-map-statuses',
            parameters={
                'successful.$': '$.[?(@.statusCode == 200)].statusCode',
                'failed.$': '$.[?(@.statusCode > 200)].statusCode',
            },
        )
        definition = evidence_creator_map_step \
            .next(evidence_creator_map_statuses_step) \
            .next(sfn.Choice(self, 'Has successful results?')
                  .when(sfn.Condition.is_present('$.successful[0]'), succeed_step)
                  .otherwise(fail_step))

        sm = sfn.StateMachine(
            self,
            self.env_context.assertions_workflow_state_machine_name,
            state_machine_name=self.env_context.name(self.env_context.assertions_workflow_state_machine_name),
            definition=definition,
            timeout=cdk.Duration.days(3),
        )
        cdk.CfnOutput(self, f'{self.env_context.name(self.env_context.assertions_workflow_state_machine_name)}-arn',
                      value=sm.state_machine_arn)
        return sm

    def _step_functions_human_input_workflow_state_machine(self):
        fail_step = sfn.Fail(self, f'{self.env_context.human_input_workflow_state_machine_name}-fail')
        sfn.Succeed(self, f'{self.env_context.human_input_workflow_state_machine_name}-succeeded')

        obfuscate_step = tasks.LambdaInvoke(
            self,
            f'{self.env_context.human_input_workflow_state_machine_name}-obfuscate',
            lambda_function=self.step_obfuscator_lambda,
            output_path='$.Payload',
        )
        statement_creator_step = tasks.LambdaInvoke(
            self,
            f'{self.env_context.human_input_workflow_state_machine_name}-statement-creator',
            lambda_function=self.step_statement_creator_lambda,
            output_path='$.Payload',
        )
        assertions_creator_step = tasks.LambdaInvoke(
            self,
            f'{self.env_context.human_input_workflow_state_machine_name}-assertions-creator',
            lambda_function=self.step_assertions_creator_lambda,
            output_path='$.Payload',
        )
        assertions_state_machine_executor_step = tasks.StepFunctionsStartExecution(
            self,
            f'{self.env_context.human_input_workflow_state_machine_name}-assertions-state-machine-executor',
            state_machine=self.assertions_workflow_state_machine,
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )
        assertions_task_token_step = tasks.LambdaInvoke(
            self,
            f'{self.env_context.human_input_workflow_state_machine_name}-assertions-creator-task-token',
            lambda_function=self.step_assertions_creator_task_token_notificator_lambda,
            integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            payload=sfn.TaskInput.from_object({
                'task_token': sfn.JsonPath.task_token,
                'body': sfn.JsonPath.string_at('$')
            }),
        )
        definition = sfn.Parallel(
            self,
            f'{self.env_context.human_input_workflow_state_machine_name}-parallel-1',
            output_path='$[0]',
        ).branch(obfuscate_step
                 .next(statement_creator_step)
                 .next(assertions_task_token_step)
                 .next(assertions_creator_step)
                 ).add_catch(fail_step) \
            .next(assertions_state_machine_executor_step)

        sm = sfn.StateMachine(
            self,
            self.env_context.human_input_workflow_state_machine_name,
            state_machine_name=self.env_context.name(self.env_context.human_input_workflow_state_machine_name),
            definition=definition,
            timeout=cdk.Duration.days(3),
        )
        cdk.CfnOutput(self, f'{self.env_context.name(self.env_context.human_input_workflow_state_machine_name)}-arn',
                      value=sm.state_machine_arn)
        return sm

    def _state_machine_cloudwatch_dashboard(self):
        dashboard = cloudwatch.Dashboard(
            self,
            'state-machine-dashboard',
            dashboard_name=self.env_context.name('state-machine'),
        )
        metrics = {
            op: {
                f'{op}-{lambda_name}': cloudwatch.Metric(
                    namespace=self.env_context.environment,
                    metric_name=self.env_context.name(f'{op}-{lambda_name}')
                )
                for lambda_name in (
                    'step-obfuscator', 'step-statement-creator', 'step-assertions-creator', 'step-evidence-creator'
                )
            }
            for op in ('load-state', 'handle', 'save-state')
        }
        width = 4
        for op in ('load-state', 'save-state'):
            metric_groups = metrics[op]
            dashboard.add_widgets(
                cloudwatch.SingleValueWidget(
                    title='',
                    metrics=list(metric_groups.values()),
                    width=24,
                )
            )

        for op in ('handle',):
            metric_groups = metrics[op]
            dashboard.add_widgets(
                *[cloudwatch.GraphWidget(
                    left=[metric],
                    width=width,
                    title=metric_name,
                ) for metric_name, metric in metric_groups.items()]
            )
