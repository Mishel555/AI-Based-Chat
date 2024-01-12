#!/bin/sh

ENV=$(echo $ENVIRONMENT_NAME | tr -d '[:space:]' | sed 's/[^[:alnum:]]//g')
STACK_BACKEND_KEY="${ENVIRONMENT_NAME}-flagship-chatbot-backend"
STACK_BASE_INFRA_KEY="${ENVIRONMENT_NAME}-flagship-chatbot-base-infra"
WS_URL_KEY="${ENV}wsapiurl"


VITE_WS_URL=$(jq -r ".[\"${STACK_BACKEND_KEY}\"][\"${WS_URL_KEY}\"]"  cdk/cdk-outputs-$ENVIRONMENT_NAME.json)
S3_BUCKET_NAME=$(jq -r ".[\"${STACK_BASE_INFRA_KEY}\"][\"staticwebsitebucketname\"]" cdk/cdk-outputs-$ENVIRONMENT_NAME.json)
echo $S3_BUCKET_NAME
echo $S3_BUCKET_NAME > bucket_name

cd frontend
case "$ENVIRONMENT_NAME" in
    staging)
        mv .env.staging.in .env.staging
        ENV_FILE=".env.staging"
        VITE_REST_URL="https://staging.chat.fsp-pi.com/"
        ;;
    production)
        mv .env.production.in .env.production
        ENV_FILE=".env.production"
        VITE_REST_URL="https://chat.fsp-pi.com/"
        ;;
    *)
        mv .env.development.in .env.development
        ENV_FILE=".env.development"
        VITE_REST_URL="https://$ENVIRONMENT_NAME-chat.fsp-pi-dev.com/"
        ;;
esac
echo "$ENV_FILE"

sed -i "s|^VITE_WS_URL=.*|VITE_WS_URL=$VITE_WS_URL/$ENVIRONMENT_NAME/|" $ENV_FILE
sed -i "s|^VITE_REST_URL=.*|VITE_REST_URL=$VITE_REST_URL|" $ENV_FILE

cat $ENV_FILE

case "$ENVIRONMENT_NAME" in
    staging)
        yarn install && yarn run staging
        ;;
    production)
        yarn install && yarn run build
        ;;
    *)
        yarn install && yarn run development
        ;;
esac