#!/bin/bash

# Default parameter values
IMAGE_NAME="hr-ui:dev-uat"
CONTAINER_APP_NAME="hr-ui-app"
DOCKERFILE_PATH="./docker/docker_file.dockerfile"
RESOURCE_GROUP="arg-syd-ing-dev-shared"
ACR_NAME="acrsydingdevkfpqjli23em5m"
CONTAINER_APP_ENVIRONMENT="ingen-container-app-env"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --image-name)
      IMAGE_NAME="$2"
      shift 2
      ;;
    --container-app-name)
      CONTAINER_APP_NAME="$2"
      shift 2
      ;;
    --dockerfile-path)
      DOCKERFILE_PATH="$2"
      shift 2
      ;;
    --resource-group)
      RESOURCE_GROUP="$2"
      shift 2
      ;;
    --acr-name)
      ACR_NAME="$2"
      shift 2
      ;;
    --container-app-environment)
      CONTAINER_APP_ENVIRONMENT="$2"
      shift 2
      ;;
    *)
      echo "Unknown parameter: $1"
      exit 1
      ;;
  esac
done

# Azure Login
echo "Logging into Azure..."
az login --tenant f23cc6fe-f058-410b-9edb-ff1b3b494e9f --use-device-code
if [ $? -ne 0 ]; then
    echo "Error: Failed to login to Azure."
    exit 1
fi

echo "Logging into ACR..."
az acr login --name $ACR_NAME
if [ $? -ne 0 ]; then
    echo "Error: Failed to login to Azure Container Registry."
    exit 1
fi

# Build the Docker image for amd64 architecture
echo "Building the Docker image for amd64 architecture..."
docker buildx create --use
if [ $? -ne 0 ]; then
    echo "Error: Failed to initialize buildx."
    exit 1
fi

docker buildx build --platform linux/amd64 -f $DOCKERFILE_PATH -t $IMAGE_NAME --output type=docker .
if [ $? -ne 0 ]; then
    echo "Error: Failed to build the Docker image."
    exit 1
fi

# Push the image to Azure Container Registry
echo "Tagging and pushing the image to Azure Container Registry..."
docker tag $IMAGE_NAME "$ACR_NAME.azurecr.io/$IMAGE_NAME"
docker push "$ACR_NAME.azurecr.io/$IMAGE_NAME"
if [ $? -ne 0 ]; then
    echo "Error: Failed to push the image to Azure Container Registry."
    exit 1
fi

# Confirmation
echo "Image successfully built for amd64, pushed to Azure"

