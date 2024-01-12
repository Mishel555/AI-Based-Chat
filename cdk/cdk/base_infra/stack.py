import typing

import aws_cdk as cdk
import aws_cdk.aws_iam as iam
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_secretsmanager as secretsmanager
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticache as elasticache

from cdk.common import EnvironmentContext

from .redis_cluster import RedisCluster
from .vpc import BaseVPC


class BaseInfraStack(cdk.Stack):
    SEC_GROUP_NAME_FORMAT = "{environment}_{group_name}_sec_group"
    SUBNET_NAME_FORMAT = "{environment}_{subnet_name}_subnet"
    
    
    def __init__(self, scope: cdk.App, env_context: EnvironmentContext, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.env_context = env_context
        self.jwt_secret_key, self.openai_secret_key = self._sm_secrets()
        self.sha_ref = self.node.get_context('sha_ref')

        self.static_website_bucket = self._static_website_bucket(self.env_context.bucket_name_static_website)
        self.request_context_bucket = self._bucket(self.env_context.bucket_name_chatbot_requests_context)
        self.chat_history_bucket = self._bucket(self.env_context.bucket_name_chatbot_chat_history)
        
        self.vpc = BaseVPC(f'{self.env_context.environment}_vpc', self)
        
        webserver_sg_name = self.SEC_GROUP_NAME_FORMAT.format(
            environment=self.env_context.environment,
            group_name="webserver"
        ) 
        self.lambdas_sec_group = ec2.SecurityGroup(
            self,
            webserver_sg_name,
            security_group_name=webserver_sg_name,
            vpc=self.vpc.vpc,
            allow_all_outbound=True,
        )
        
        private_subnets_ids = [ps.subnet_id for ps in self.vpc.vpc.private_subnets]
        self.redis_subnet_group = elasticache.CfnSubnetGroup(
            self,
            self.SUBNET_NAME_FORMAT.format(
                environment=self.env_context.environment,
                subnet_name='redis'
            ),
            subnet_ids=private_subnets_ids,
            description="subnet group for redis",
        )
        
        redis_sg_name = self.SEC_GROUP_NAME_FORMAT.format(
            environment=self.env_context.environment,
            group_name="redis"
        )
        self.redis_sec_group = ec2.SecurityGroup(
            self,
            redis_sg_name,
            security_group_name=redis_sg_name,
            vpc=self.vpc.vpc,
            allow_all_outbound=True,
        )
        self.redis_sec_group.add_ingress_rule(
            peer=self.lambdas_sec_group,
            description="Allow Redis connection",
            connection=ec2.Port.tcp(6379),
        )
        self.cache_cluster = RedisCluster(
            self,
            f"{self.env_context.environment}_cache_cluster",
            self.redis_subnet_group,
            security_group_ids=[self.redis_sec_group.security_group_id]
        )
        
        self.common_envs = {
            "REDIS_HOST": self.env_context.redis_host
            or self.cache_cluster.redis.attr_redis_endpoint_address,
            "REDIS_PORT": self.env_context.redis_port
            or self.cache_cluster.redis.attr_redis_endpoint_port,
            "AUTH0_CALLBACK": self.env_context.auth0_login_callback,
            "LOG_APIGW_EVENT": self.env_context.log_apigw_event,
            "CLIENT_ID": self.env_context.auth0_client_id,
            "AUTH0_URL": self.env_context.auth0_url,
            "ACCESS_KEY_AUDIENCE": self.env_context.access_key_audience,
        }
        
        self._adjust_policies()

    def _static_website_bucket(self, bucket_name: str) -> s3.Bucket:
        bucket = self._bucket(bucket_name)
        apigw_principal = cdk.aws_iam.ServicePrincipal('apigateway.amazonaws.com')
        role = iam.Role(
            self,
            'api-gateway-role',
            role_name=self.env_context.name('api-gateway-role'),
            assumed_by=apigw_principal
        )
        self.static_website_bucket_role = role
        role.add_to_policy(iam.PolicyStatement(
            actions=['s3:*'],
            resources=[bucket.bucket_arn],
        ))
        role.add_to_policy(iam.PolicyStatement(
            actions=['s3:*'],
            resources=[bucket.arn_for_objects('*')],
        ))
        return bucket

    def _sm_secrets(self) -> typing.Tuple:
        jwt_secret_key = secretsmanager.Secret.from_secret_complete_arn(
            self,
            'jwt-secret-key',
            secret_complete_arn=self.env_context.jwt_secret_key_full_arn,
        )
        openai_secret_key = secretsmanager.Secret.from_secret_complete_arn(
            self,
            'openai-secret-key',
            secret_complete_arn=self.env_context.openai_secret_key_full_arn,
        )
        return jwt_secret_key, openai_secret_key

    def _bucket(self, bucket_name: str) -> s3.Bucket:
        bucket_id = self.env_context.unique_env_suffix
        removal_policy = cdk.RemovalPolicy.DESTROY if self.env_context.is_dev else cdk.RemovalPolicy.RETAIN
        bucket = s3.Bucket(
            self,
            self.env_context.name(bucket_name),
            bucket_name=self.env_context.name(f'{bucket_name}-{bucket_id}'),
            auto_delete_objects=self.env_context.is_dev,
            removal_policy=removal_policy,
        )
        cdk.CfnOutput(self, f'{bucket_name}-bucket-name', value=bucket.bucket_name)
        return bucket

    def _adjust_policies(self):
        pass
