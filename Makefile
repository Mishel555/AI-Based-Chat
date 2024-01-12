version=$(shell git rev-parse --short HEAD)

.PHONY: build_auth, push_auth, run_auth_local

help:
	@echo "Available targets:"
	@echo "  build_auth         Build the authentication-related Lambda functions"
	@echo "  push_auth          Push the authentication-related Lambda functions to the ECR repository"
	@echo "  run_auth_local     Run the authentication API locally using AWS SAM"
	@echo "  clean_auth_containers    Remove authentication-related Docker containers"
	@echo "  help               Display this help message"

docker_auth:
	@if [ -z "$(ECR_REPOSITORY_URL)" ]; then echo "ERROR: ECR_REPOSITORY_URL is not specified"; exit 1; fi
	aws ecr get-login-password | docker login --username AWS --password-stdin $(ECR_REPOSITORY_URL)


build_docker_base:
	docker build -t flagship-chatbot-base-conda-env-py3.9:latest . -f base-docker/Dockerfile.in
	docker build -t flagship-chatbot-aws-lambda-base-conda-env-py3.9:latest . -f sam/base-docker/Dockerfile.in



_ecr_repository_defined:
	@if [ -z "$(ECR_REPOSITORY_URL)" ]; then echo "ERROR: ECR_REPOSITORY_URL is not specified"; exit 1; fi


_env_name_defined:
	@if [ -z "$(ENV_NAME)" ]; then echo "ERROR: ENV_NAME is not specified"; exit 1; fi



auth_env: _ecr_repository_defined
	$(eval login_lambda_container_name := $(ECR_REPOSITORY_URL)/flagship-chatbot-aws-lambda-api-login-py3.9:$(version))
	$(eval login_callback_lambda_container_name := $(ECR_REPOSITORY_URL)/flagship-chatbot-aws-lambda-api-login-callback-py3.9:$(version))
	$(eval logout_lambda_container_name := $(ECR_REPOSITORY_URL)/flagship-chatbot-aws-lambda-api-logout-py3.9:$(version))


vector_store_env: _ecr_repository_defined
	$(eval vector_store_container_name := $(ECR_REPOSITORY_URL)/flagship-chatbot-vector-store-faissdb-py3.9:$(version))


api_env: _ecr_repository_defined
	
	$(eval api_start_chat_container_name := $(ECR_REPOSITORY_URL)/flagship-chatbot-aws-lambda-api-start-chat-py3.9:$(version))

	$(eval ws_api_container_name := $(ECR_REPOSITORY_URL)/flagship-chatbot-aws-lambda-ws-api-py3.9:${version})
	$(eval ws_api_human_input_container_name := $(ECR_REPOSITORY_URL)/flagship-chatbot-aws-lambda-ws-api-human-input-py3.9:${version})
	$(eval ws_api_custom_assertion_container_name := $(ECR_REPOSITORY_URL)/flagship-chatbot-aws-lambda-ws-api-custom-assertion-py3.9:${version})
	
	$(eval api_step_obpuscator_container_name := $(ECR_REPOSITORY_URL)/flagship-chatbot-aws-lambda-step-obfuscator-py3.9:${version})
	$(eval step_statement_container_name := $(ECR_REPOSITORY_URL)/flagship-chatbot-aws-lambda-step-statement-creator-py3.9:${version})
	$(eval step_assertions_container_name := $(ECR_REPOSITORY_URL)/flagship-chatbot-aws-lambda-step-assertions-creator-py3.9:${version})
	$(eval step_evidence_creator_container_name := $(ECR_REPOSITORY_URL)/flagship-chatbot-aws-lambda-step-evidence-creator-py3.9:${version})


build_api: api_env
	docker build -t $(api_start_chat_container_name) . -f sam/func_api_start_chat/Dockerfile.in

	docker build -t $(ws_api_container_name) . -f sam/func_ws_api/Dockerfile.in
	docker build -t $(ws_api_human_input_container_name) . -f sam/func_ws_api_human_input/Dockerfile.in
	docker build -t $(ws_api_custom_assertion_container_name) . -f sam/func_ws_api_custom_assertion/Dockerfile.in

	docker build -t $(api_step_obpuscator_container_name) . -f sam/func_step_obfuscator/Dockerfile.in
	docker build -t $(step_statement_container_name) . -f sam/func_step_statement_creator/Dockerfile.in
	docker build -t $(step_assertions_container_name) . -f sam/func_step_assertions_creator/Dockerfile.in
	docker build -t $(step_evidence_creator_container_name) . -f sam/func_step_evidence_creator/Dockerfile.in


build_vector_store: vector_store_env
	docker build -t $(vector_store_container_name) . -f python/vector_store_faissdb/Dockerfile.in	


build_login: auth_env
	@echo "Building $(login_lambda_container_name)"
	@docker build --no-cache -t $(login_lambda_container_name) . -f sam/func_api_login/Dockerfile.in

build_login_callback: auth_env
	@echo "Building $(login_callback_lambda_container_name)"
	@docker build --no-cache -t $(login_callback_lambda_container_name) . -f sam/func_api_login_callback/Dockerfile.in


build_logout: auth_env 
	@echo "Building $(logout_lambda_container_name)"
	@docker build --no-cache -t $(logout_lambda_container_name) . -f sam/func_api_logout/Dockerfile.in


build_auth: build_login build_login_callback build_logout


build: build_auth build_api


clean_auth_containers: auth_env
	@if docker images -q $(login_lambda_container_name) > /dev/null; then docker rmi $(login_lambda_container_name); fi
	@if docker images -q $(login_callback_lambda_container_name) > /dev/null; then docker rmi $(login_callback_lambda_container_name); fi
	@if docker images -q $(logout_lambda_container_name) > /dev/null; then docker rmi $(logout_lambda_container_name); fi


push_auth: auth_env
	@docker push $(login_lambda_container_name) &
	@docker push $(login_callback_lambda_container_name) &
	@docker push $(logout_lambda_container_name) &


push_api: api_env
	docker push $(api_start_chat_container_name) &

	docker push $(ws_api_container_name) &
	docker push $(ws_api_human_input_container_name) &
	docker push $(ws_api_custom_assertion_container_name) &

	docker push $(api_step_obpuscator_container_name) &
	docker push $(step_statement_container_name) &
	docker push $(step_assertions_container_name) &
	docker push $(step_evidence_creator_container_name)
	

push: push_auth push_api
