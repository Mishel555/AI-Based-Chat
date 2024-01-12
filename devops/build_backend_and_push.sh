#!/bin/bash

export DOCKER_REPO_NAME=flagship-chatbot-conda-env-py3.9
export BASE_PREFIX=base
export BASE_AWS_LAMBDA_PREFIX=aws_lambda_base
export BASE_DOCKER_REPO_NAME=$DOCKER_REPO_NAME
export BASE_DOCKER_AWS_LAMBDA_REPO_NAME=$DOCKER_REPO_NAME


base_docker_ecr_tag() {

  echo "$ECR_REGISTRY/$BASE_DOCKER_REPO_NAME:${BASE_PREFIX}-${version}"
}

base_docker_latest_tag() {
  echo "$BASE_DOCKER_REPO_NAME:${BASE_PREFIX}-latest"
}

base_aws_lambda_docker_ecr_tag() {
  echo "$ECR_REGISTRY/$BASE_DOCKER_AWS_LAMBDA_REPO_NAME:${BASE_AWS_LAMBDA_PREFIX}-${version}"
}

base_aws_lambda_docker_latest_tag() {
  echo "$BASE_DOCKER_AWS_LAMBDA_REPO_NAME:${BASE_AWS_LAMBDA_PREFIX}-latest"
}

docker_images_deploy_base() {

  export BASE_DOCKER_LATEST_TAG_NAME=$(base_docker_latest_tag)
  export BASE_DOCKER_ECR_TAG_NAME=$(base_docker_ecr_tag)

  docker build -t $BASE_DOCKER_LATEST_TAG_NAME . -f base-docker/Dockerfile
  docker tag $BASE_DOCKER_LATEST_TAG_NAME $BASE_DOCKER_ECR_TAG_NAME
  docker push $BASE_DOCKER_ECR_TAG_NAME
}

docker_images_deploy() {

  export BASE_DOCKER_LATEST_TAG_NAME=$(base_docker_latest_tag)
  export BASE_DOCKER_ECR_TAG_NAME=$(base_docker_ecr_tag)
  export BASE_DOCKER_AWS_LAMBDA_LATEST_NAME=$(base_aws_lambda_docker_latest_tag)
  export BASE_DOCKER_AWS_LAMBDA_ECR_TAG_NAME=$(base_aws_lambda_docker_ecr_tag)

  sed "s#$BASE_DOCKER_LATEST_TAG_NAME#$BASE_DOCKER_ECR_TAG_NAME#g" sam/base-docker/Dockerfile.in >sam/base-docker/Dockerfile
  docker build -t $BASE_DOCKER_AWS_LAMBDA_LATEST_NAME . -f sam/base-docker/Dockerfile.in
  docker tag $BASE_DOCKER_AWS_LAMBDA_LATEST_NAME $BASE_DOCKER_AWS_LAMBDA_ECR_TAG_NAME
  docker push $BASE_DOCKER_AWS_LAMBDA_ECR_TAG_NAME

  declare -A ecr_repositories_with_docker_files
  ecr_repositories_with_docker_files["aws-lambda-api-start-chat"]="sam/func_api_start_chat/Dockerfile"
  ecr_repositories_with_docker_files["aws-lambda-api"]="sam/func_ws_api/Dockerfile"
  ecr_repositories_with_docker_files["aws-lambda-api-human-input"]="sam/func_ws_api_human_input/Dockerfile"
  ecr_repositories_with_docker_files["aws-lambda-api-custom-assertion"]="sam/func_ws_api_custom_assertion/Dockerfile"
  ecr_repositories_with_docker_files["aws-lambda-api-task-token"]="sam/func_ws_api_task_token/Dockerfile"
  ecr_repositories_with_docker_files["aws-lambda-step-task-token-notificator"]="sam/func_step_task_token_notificator/Dockerfile"
  ecr_repositories_with_docker_files["aws-lambda-step-obfuscator"]="sam/func_step_obfuscator/Dockerfile"
  ecr_repositories_with_docker_files["aws-lambda-step-statement-creator"]="sam/func_step_statement_creator/Dockerfile"
  ecr_repositories_with_docker_files["aws-lambda-step-assertions-creator"]="sam/func_step_assertions_creator/Dockerfile"
  ecr_repositories_with_docker_files["aws-lambda-step-evidence-creator"]="sam/func_step_evidence_creator/Dockerfile"
  ecr_repositories_with_docker_files["aws-lambda-api-login"]="sam/func_api_login/Dockerfile"
  ecr_repositories_with_docker_files["aws-lambda-api-login-callback"]="sam/func_api_login_callback/Dockerfile"
  ecr_repositories_with_docker_files["aws-lambda-api-user"]="sam/func_api_user/Dockerfile"
  ecr_repositories_with_docker_files["aws-lambda-api-logout"]="sam/func_api_logout/Dockerfile"
  ecr_repositories_with_docker_files["aws-lambda-api-user"]="sam/func_api_user/Dockerfile"
  #  ecr_repositories_with_docker_files["aws-lambda-vector-store-faissdb"]="python/vector_store_faissdb/Dockerfile"

  for k in "${!ecr_repositories_with_docker_files[@]}"; do
    echo "Building $ECR_REGISTRY/$BASE_DOCKER_AWS_LAMBDA_REPO_NAME:${k}-${version}"
    sed "s#$BASE_DOCKER_AWS_LAMBDA_LATEST_NAME#$BASE_DOCKER_AWS_LAMBDA_ECR_TAG_NAME#g" ${ecr_repositories_with_docker_files[$k]}.in >${ecr_repositories_with_docker_files[$k]}
    docker build -t $BASE_DOCKER_AWS_LAMBDA_REPO_NAME/${k}-latest . -f ${ecr_repositories_with_docker_files[$k]}
    docker tag $BASE_DOCKER_AWS_LAMBDA_REPO_NAME/${k}-latest $ECR_REGISTRY/$BASE_DOCKER_AWS_LAMBDA_REPO_NAME:${k}-${version}
  done
  for k in "${!ecr_repositories_with_docker_files[@]}"; do
    echo "Pushing $ECR_REGISTRY/$BASE_DOCKER_AWS_LAMBDA_REPO_NAME:${k}-${version}"
    docker push $ECR_REGISTRY/$BASE_DOCKER_AWS_LAMBDA_REPO_NAME:${k}-${version}
  done

}