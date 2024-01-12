from aws_cdk import Stack
from aws_cdk import aws_elasticache as elasticache


class RedisCluster:
    def __init__(
        self, 
        stack: Stack,
        cluster_name: str,
        subnet: elasticache.CfnSubnetGroup,
        security_group_ids: list[str],
        node_type: str = "cache.t2.micro",
        engine: str = "redis",
        num_cache_nodes: int = 1,
    ):
        self._stack = stack
        self._subnet = subnet
        self._redis = self._create_redis(
            cluster_name,
            security_group_ids,
            node_type,
            engine,
            num_cache_nodes,
        )
        
    @property
    def redis(self) -> elasticache.CfnCacheCluster:
        return self._redis

    def _create_redis(
        self,
        cluster_name: str,
        security_groups: list[int],
                node_type: str,
        engine: str,
        num_cache_nodes: int,
    ) -> elasticache.CfnCacheCluster:
        return elasticache.CfnCacheCluster(
            self._stack,
            cluster_name,
            cache_node_type=node_type,
            engine=engine,
            num_cache_nodes=num_cache_nodes,
            vpc_security_group_ids=security_groups,
            cache_subnet_group_name=self._subnet.ref,
        )
