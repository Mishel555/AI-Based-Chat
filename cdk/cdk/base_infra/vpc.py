import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2


class BaseVPC:
    def __init__(self, vpc_name: str, stack: cdk.Stack):
        self._stack = stack
        self._vpc = self._create_vpc(vpc_name)

    @property
    def vpc(self) -> cdk.Stack:
        return self._vpc

    def _create_vpc(self, vpc_name: str) -> cdk.aws_ec2.Vpc:
        vpc = ec2.Vpc(
            self._stack,
            vpc_name,
            nat_gateways=1,
            cidr="10.0.0.0/16",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
        )
        return vpc
