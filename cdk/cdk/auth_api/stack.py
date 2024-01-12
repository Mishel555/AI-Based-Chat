import aws_cdk as cdk

from cdk.base_infra import BaseInfraStack

from .rest_api import AuthRESTApi


class AuthAPIStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.App,
        base_infra_stack: BaseInfraStack,
        construct_id: str,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)
        self.env_context = base_infra_stack.env_context
        self.sha_ref = self.node.get_context("sha_ref")
        self.jwt_key_secret = base_infra_stack.jwt_secret_key

        self.vpc = base_infra_stack.vpc.vpc

        self.redis = base_infra_stack.cache_cluster.redis

        self.rest_api = AuthRESTApi(
            self,
            self.vpc,
            security_groups=[base_infra_stack.lambdas_sec_group],
            env_context=self.env_context,
            envs={
                "REDIRECT_EXTRA_PATH": self.env_context.api_redirect_extra_path,
                **base_infra_stack.common_envs
            },
            sha_ref=self.sha_ref,
            jwt_key_name=self.jwt_key_secret.secret_name
        )
        self._adjust_policies()

    def _adjust_policies(self):
        self.jwt_key_secret.grant_read(self.rest_api.api_login_callback)
        self.jwt_key_secret.grant_read(self.rest_api.api_logout)
        self.jwt_key_secret.grant_read(self.rest_api.api_user)
