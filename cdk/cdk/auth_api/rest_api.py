from typing import Any, Optional

import aws_cdk as cdk
import aws_cdk.aws_cloudwatch as cloudwatch
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_lambda as lambda_
from aws_cdk import aws_ec2 as ec2

from ..common import EnvironmentContext


class AuthRESTApi:
    def __init__(
            self,
            stack: cdk.Stack,
            vpc: ec2.Vpc,
            env_context: EnvironmentContext,
            envs: dict[str, Any],
            sha_ref: str,
            jwt_key_name: str,
            security_groups: Optional[list[ec2.SecurityGroup]] = None,
    ):
        self._stack = stack
        self.sha_ref = sha_ref

        self.env_context = env_context
        self.vpc = vpc
        self.security_groups = security_groups

        self._init_lambdas(envs)

    def _init_lambdas(self, envs: dict[str, Any]):
        login_envs = {**envs}
        self.api_login = self._api_lambda(
            "api-login-lambda",
            self.env_context.ecr_name_lambda_api_login_lambda,
            self.env_context.image_tag_prefix_lambda_api_login,
            login_envs,
        )

        callback_envs = {
            **envs,
            "SUCCESS_LOGIN_REDIRECT_PATH": self.env_context.success_login_redirect_path
        }
        self.api_login_callback = self._api_lambda(
            "api-login-callback-lambda",
            self.env_context.ecr_name_lambda_api_login_callback_lambda,
            self.env_context.image_tag_prefix_lambda_api_login_callback,
            callback_envs,
        )

        logout_envs = {**envs}
        self.api_logout = self._api_lambda(
            "api-logout-lambda",
            self.env_context.ecr_name_lambda_api_logout_lambda,
            self.env_context.image_tag_prefix_lambda_api_logout,
            logout_envs,
        )
        
        user_handler_envs = {**envs}
        self.api_user = self._api_lambda(
            "user-handler-lambda",
            self.env_context.ecr_name_lambda_api_user_handler_lambda,
            self.env_context.image_tag_prefix_lambda_api_user,
            user_handler_envs,
        )

    def _api_lambda(
            self, lambda_name: str, ecr_name: str, tag_prefix: str = None, env_variables: dict = None
    ) -> lambda_.Function:
        ecr_repo = ecr.Repository.from_repository_name(
            self._stack,
            f"{lambda_name}-ecr-repo",
            ecr_name,
        )
        cloudwatch.Metric(
            namespace=self.env_context.environment,
            metric_name=self.env_context.name(lambda_name),
        )
        return lambda_.Function(
            self._stack,
            lambda_name,
            function_name=self.env_context.name(lambda_name),
            runtime=lambda_.Runtime.FROM_IMAGE,
            code=lambda_.Code.from_ecr_image(
                ecr_repo,
                tag_or_digest=f'{tag_prefix}-{self.sha_ref}' if tag_prefix else self.sha_ref,
            ),
            handler=lambda_.Handler.FROM_IMAGE,
            environment={
                "POWERTOOLS_METRICS_NAMESPACE": self.env_context.environment,
                "POWERTOOLS_SERVICE_NAME": self.env_context.name(lambda_name),
                **(env_variables or {})
            },
            memory_size=256,
            timeout=cdk.Duration.seconds(29),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=self.security_groups,
        )
