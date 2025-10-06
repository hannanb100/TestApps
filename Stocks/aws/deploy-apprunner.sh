#!/bin/bash
# AWS App Runner Deployment Script
# This script automates the deployment process to AWS App Runner

set -e  # Exit if any command fails

echo "🚀 Deploying AI Stock Tracking Agent to AWS App Runner..."

# Configuration - You can change these values
AWS_REGION="us-east-1"  # Change this to your preferred AWS region
ECR_REPOSITORY_NAME="ai-stock-tracker"
APP_RUNNER_SERVICE_NAME="ai-stock-tracker"

# Get AWS Account ID automatically
echo "📋 Getting AWS Account ID..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "   AWS Account ID: $AWS_ACCOUNT_ID"

# Build the ECR repository URI
ECR_REPOSITORY_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}"
echo "   ECR Repository URI: $ECR_REPOSITORY_URI"

echo ""
echo "📦 Building Docker image..."
docker build -t ${ECR_REPOSITORY_NAME} .

echo ""
echo "🏷️ Tagging image for ECR..."
docker tag ${ECR_REPOSITORY_NAME}:latest ${ECR_REPOSITORY_URI}:latest

echo ""
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY_URI}

echo ""
echo "📤 Pushing image to ECR..."
docker push ${ECR_REPOSITORY_URI}:latest

echo ""
echo "🚀 Creating App Runner service..."
echo "   This may take a few minutes..."

# Update the config file with the actual ECR URI
sed "s/YOUR_ECR_REPOSITORY_URI/${ECR_REPOSITORY_URI}/g" aws/apprunner-config.json > aws/apprunner-config-updated.json

# Create the App Runner service
aws apprunner create-service \
    --service-name ${APP_RUNNER_SERVICE_NAME} \
    --source-configuration file://aws/apprunner-config-updated.json \
    --instance-configuration '{
        "Cpu": "1 vCPU",
        "Memory": "2 GB"
    }' \
    --region ${AWS_REGION}

echo ""
echo "✅ Deployment initiated!"
echo "🌐 Your app will be available at: https://${APP_RUNNER_SERVICE_NAME}-${AWS_ACCOUNT_ID}.${AWS_REGION}.awsapprunner.com"
echo ""
echo "📊 To check deployment status:"
echo "   aws apprunner describe-service --service-arn \$(aws apprunner list-services --query 'ServiceSummaryList[?ServiceName==\`${APP_RUNNER_SERVICE_NAME}\`].ServiceArn' --output text) --region ${AWS_REGION}"
echo ""
echo "🗑️ To delete the service later:"
echo "   aws apprunner delete-service --service-arn \$(aws apprunner list-services --query 'ServiceSummaryList[?ServiceName==\`${APP_RUNNER_SERVICE_NAME}\`].ServiceArn' --output text) --region ${AWS_REGION}"
