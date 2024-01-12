import boto3

# from aws_lambda_powertools.utilities import parameters
# endpoint_comments: str = parameters.get_parameter('/chatbot/endpoint_comments')

def region():
    # TODO: externalize region
    return 'us-east-1'


__apigw_mgmt_client = None
__s3_client = None
__secretsmanager_client = None
__stepfunctions_client = None


def apigw_mgmt(**kwargs):
    global __apigw_mgmt_client
    if not __apigw_mgmt_client:
        # TODO: check if with disabled execute API this URL functions.
        #  If not, use domainName from requestContext, alternatively, inject endpoint URL through CDK deployment
        endpoint_url = 'https://{apiId}.execute-api.{region}.amazonaws.com/{stage}'.format(
            region=region(), **kwargs,
        )
        __apigw_mgmt_client = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint_url, region_name=region())
    return __apigw_mgmt_client


def apigw_by_endpoint_url(endpoint_url: str):
    global __apigw_mgmt_client
    if not __apigw_mgmt_client:
        __apigw_mgmt_client = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint_url, region_name=region())
    return __apigw_mgmt_client


def s3():
    global __s3_client
    if not __s3_client:
        __s3_client = boto3.client('s3', region_name=region())
    return __s3_client


def secretsmanager():
    global __secretsmanager_client
    if not __secretsmanager_client:
        __secretsmanager_client = boto3.client('secretsmanager', region_name=region())
    return __secretsmanager_client


def stepfunctions():
    global __stepfunctions_client
    if not __stepfunctions_client:
        __stepfunctions_client = boto3.client('stepfunctions', region_name=region())
    return __stepfunctions_client


def write_str_to_s3(bucket_name, object_key, value: str) -> None:
    s3().put_object(Bucket=bucket_name, Key=object_key, Body=value.encode('utf-8'))


def read_str_from_s3(bucket_name, object_key) -> str:
    data = s3().get_object(Bucket=bucket_name, Key=object_key)['Body'].read()
    return data.decode('utf-8')


def get_secret(secret_id: str) -> str:
    result = secretsmanager().get_secret_value(SecretId=secret_id)
    return result['SecretString']


def start_sfn_workflow(**kwargs) -> dict:
    return stepfunctions().start_execution(**kwargs)


def resume_sfn_workflow(**kwargs) -> dict:
    return stepfunctions().send_task_success(**kwargs)
