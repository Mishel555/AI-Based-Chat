import typing

import aws_cdk as cdk
import aws_cdk.aws_cloudwatch as cloudwatch
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_ecs_patterns as ecs_patterns
import aws_cdk.aws_logs as logs
from aws_cdk.aws_ecs import ScalableTaskCount

from cdk.base_infra import BaseInfraStack
from cdk.common import EnvironmentContext


class VectorStoreStack(cdk.Stack):
    def __init__(self, scope: cdk.App, env_context: EnvironmentContext,
                 base_infra_stack: BaseInfraStack,
                 construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.env_context = env_context
        self.sha_ref = self.node.get_context('sha_ref')
        self.openai_secret_key = base_infra_stack.openai_secret_key

        self.vpc = base_infra_stack.vpc.vpc
        self._configure_vpc()

        self.cluster = self._cluster()
        self.alb_service, self.service_task_count = self._service()
        self._adjust_policies()
        self._cloudwatch_dashboard()

    def _adjust_policies(self):
        pass

    def _configure_vpc(self) -> ec2.Vpc:
        vpc = self.vpc
        vpc.add_gateway_endpoint(
            'S3GatewayVpcEndpoint',
            service=ec2.GatewayVpcEndpointAwsService.S3,
        )
        vpc.add_interface_endpoint(
            'CloudWatchVpcEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH,
        )
        vpc.add_interface_endpoint(
            'CloudWatchLogsVpcEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
        )
        vpc.add_interface_endpoint(
            'EcrDockerVpcEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
        )
        vpc.add_interface_endpoint(
            'EcrVpcEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.ECR,
        )
        vpc.add_interface_endpoint(
            'SecretsManagerVpcEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
        )
        return vpc

    def _cluster(self) -> ecs.Cluster:
        return ecs.Cluster(self, self.env_context.name('chatbot-ecs-cluster'), vpc=self.vpc)

    def _service(self) -> typing.Tuple[ecs_patterns.ApplicationLoadBalancedServiceBase, ScalableTaskCount]:
        log_group_id = self.env_context.unique_env_suffix

        task_definition = ecs.FargateTaskDefinition(
            self,
            'chatbot-vector-store-faissdb',
            family='chatbot-vector-store',
            cpu=self.env_context.vector_store_cpu_units,
            memory_limit_mib=self.env_context.vector_store_memory_limit_mib,
        )
        ecr_repo = ecr.Repository.from_repository_name(
            self,
            'vector-store-faissdb-ecr-repo',
            self.env_context.ecr_name_vector_store_faissdb,
        )
        log_group = logs.LogGroup(
            self,
            'faissdb-log-group',
            log_group_name=f'/aws/ecs/{self.env_context.name("faissdb-log-group")}-{log_group_id}',
            removal_policy=cdk.RemovalPolicy.DESTROY if self.env_context.is_dev else cdk.RemovalPolicy.RETAIN,
            retention=logs.RetentionDays.FIVE_DAYS if self.env_context.is_dev else logs.RetentionDays.INFINITE,
        )
        tag_prefix = self.env_context.image_tag_prefix_vector_store_faissdb
        task_definition.add_container(
            'faissdb',
            image=ecs.ContainerImage.from_ecr_repository(
                repository=ecr_repo,
                tag=f'{tag_prefix}-{self.sha_ref}' if tag_prefix else self.sha_ref,
            ),
            container_name='faissdb',
            logging=ecs.LogDrivers.aws_logs(
                log_group=log_group,
                stream_prefix='faissdb',
            ),
            port_mappings=[ecs.PortMapping(container_port=80)],
            health_check=ecs.HealthCheck(
                command=['CMD-SHELL', '/usr/bin/curl -f http://localhost/health || exit 1'],
                interval=cdk.Duration.seconds(30),
                retries=3,
                start_period=cdk.Duration.seconds(30),
                timeout=cdk.Duration.seconds(10),
            ),
            environment={
                'CORPUS_DB_PATH': '/faissdb-store',
                'ECS_AVAILABLE_LOGGING_DRIVERS': '["json-file","awslogs"]',
            },
            secrets={
                'OPENAI_API_KEY': ecs.Secret.from_secrets_manager(self.openai_secret_key),
            },
        )
        alb_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            'faissdb-service',
            cluster=self.cluster,
            desired_count=self.env_context.vector_store_desired_tasks_count,
            task_definition=task_definition,
            enable_execute_command=True,
            idle_timeout=cdk.Duration.minutes(5),
            assign_public_ip=False,
            # public_load_balancer=False,
        )
        alb_service.target_group.configure_health_check(
            path='/health',
            interval=cdk.Duration.seconds(30),
            unhealthy_threshold_count=3,
            timeout=cdk.Duration.seconds(10),
        )
        service_task_count = alb_service.service.auto_scale_task_count(
            max_capacity=self.env_context.vector_store_max_tasks_count,
        )
        cdk.CfnOutput(self, 'faissdb-dns-name', value=alb_service.load_balancer.load_balancer_dns_name)

        return alb_service, service_task_count

    def _cloudwatch_dashboard(self):
        dashboard = cloudwatch.Dashboard(
            self,
            'vector-store-dashboard',
            dashboard_name=self.env_context.name('vector-store'),
        )
        cpu_utilization_metric = self.alb_service.service.metric_cpu_utilization(
            period=cdk.Duration.minutes(1),
            label='CPU Utilization',
        )
        memory_utilization_metric = self.alb_service.service.metric_memory_utilization(
            period=cdk.Duration.minutes(1),
            label='Memory Utilization',
        )
        alb_request_count_metric = self.alb_service.load_balancer.metrics.request_count(
            period=cdk.Duration.minutes(1),
            label='LB Request Count',
        )
        target_group_request_count_metric = self.alb_service.target_group.metrics.request_count(
            period=cdk.Duration.minutes(1),
            label='Target Group Request Count',
        )
        request_count_per_target_metric = self.alb_service.target_group.metrics.request_count_per_target(
            period=cdk.Duration.minutes(1),
            statistic=str(cloudwatch.Statistic.SUM.value),
            label='Target Request Count',
        )
        healthy_host_count_metric = self.alb_service.target_group.metrics.healthy_host_count(
            period=cdk.Duration.minutes(1),
            label='Healthy Tasks',
        )
        dashboard.add_widgets(
            cloudwatch.SingleValueWidget(
                title='Current Values',
                metrics=[
                    cpu_utilization_metric,
                    memory_utilization_metric,
                    healthy_host_count_metric,
                    alb_request_count_metric,
                    target_group_request_count_metric,
                    request_count_per_target_metric,
                ],
                width=24,
            ),
            cloudwatch.GraphWidget(
                left=[cpu_utilization_metric],
                width=8,
                title='CPU Utilization',
            ),
            cloudwatch.GraphWidget(
                left=[memory_utilization_metric],
                width=8,
                title='Memory Utilization',
            ),
            cloudwatch.GraphWidget(
                left=[healthy_host_count_metric],
                width=8,
                title='Healthy Tasks',
            ),
            cloudwatch.GraphWidget(
                left=[alb_request_count_metric],
                width=8,
                title='LB Request Count',
            ),
            cloudwatch.GraphWidget(
                left=[target_group_request_count_metric],
                width=8,
                title='Target Group Request Count',
            ),
            cloudwatch.GraphWidget(
                left=[request_count_per_target_metric],
                width=8,
                title='Target Request Count',
            ),
        )
