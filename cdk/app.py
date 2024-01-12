#!/usr/bin/env python3

import aws_cdk as cdk

from cdk.auth_api import AuthAPIStack
from cdk.backend import BackendStack
from cdk.base_infra import BaseInfraStack
from cdk.common import load_environment_context
from cdk.common_api import CommonAPIStack

app = cdk.App()
env_context = load_environment_context(app)

base_infra_stack = BaseInfraStack(
    app,
    env_context,
    env_context.name('flagship-chatbot-base-infra')
)

auth_api_stack = AuthAPIStack(
    app,
    base_infra_stack,
    env_context.name('flagship-chatbot-auth-api'),
)

backend_stack = BackendStack(
    app,
    base_infra_stack,
    env_context.name('flagship-chatbot-backend')
)

common_api_stack = CommonAPIStack(
    app,
    env_context.name('flagship-chatbot-common-api'),
    base_infra_stack,
    auth_api_stack,
    backend_stack,
)

app.synth()
