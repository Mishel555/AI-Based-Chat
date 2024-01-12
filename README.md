Environment name (one of the followings):

```shell
export ENV_NAME=dev-ui
```

Secret values:

```shell
export JWT_SECRET_KEY=blah
export OPENAI_SECRET_KEY=blah
```

Create secrets in Secrets Manager:

```shell
aws secretsmanager create-secret --name "${ENV_NAME}-jwt-secret-key" --secret-string "$JWT_SECRET_KEY"
aws secretsmanager create-secret --name "${ENV_NAME}-openai-secret-key" --secret-string "$OPENAI_SECRET_KEY"
```

Create ECR repositories:

```shell
aws ecr create-repository --repository-name $DOCKER_REPO_NAME --image-tag-mutability IMMUTABLE --image-scanning-configuration scanOnPush=true --region $AWS_DEFAULT_REGION || true

export DOCKER_REPO_NAME=flagship-chatbot-conda-env-py3.9

```

Setup local docker to auth to ECR:

```shell
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY_URL
```

Export conda env:

```shell
conda env export --no-build --file base-docker/vamo-conda-env.yml
```


#### Pre-commit

Install pre-commit:

```shell
pip install pre-commit
pre-commit install
```
