# Deploying MeccaAI on AWS Bedrock

This guide explains how to deploy MeccaAI using AWS Bedrock models instead of OpenAI.

## Prerequisites

1. **AWS Account** with Bedrock access
2. **AWS CLI** installed and configured
3. **Bedrock Model Access** - Request access to Claude models in AWS Bedrock console

## Setup Instructions

### 1. Enable Bedrock Model Access

1. Navigate to the AWS Bedrock console
2. Go to "Model access" in the left sidebar
3. Request access to the following models:
   - Anthropic Claude 3.5 Sonnet v2
   - (Add other models as needed)

### 2. Configure AWS Credentials

Choose one of these methods:

#### Option A: AWS CLI Configuration
```bash
aws configure
```

#### Option B: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

#### Option C: AWS Profile
```bash
export AWS_PROFILE=your-profile-name
```

### 3. Set Up Environment

1. Copy the Bedrock environment file:
```bash
cp .env.bedrock.example .env.bedrock
```

2. Edit `.env.bedrock` with your credentials:
```bash
ENVIRONMENT=bedrock
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
```

3. Load the environment:
```bash
source .env.bedrock
# or
export $(cat .env.bedrock | xargs)
```

### 4. Install Dependencies

```bash
uv add boto3
```

### 5. Test the Installation

```bash
# List available agents
uv run python -m meccaai.apps.lumos_bedrock_app list-agents

# Test a simple query
uv run python -m meccaai.apps.lumos_bedrock_app chat "Hello, introduce yourself"

# Test semantic layer
uv run python -m meccaai.apps.lumos_bedrock_app chat "what is total sales amount for sales channel code L098 on 2025-08-10?"

# Start interactive mode
uv run python -m meccaai.apps.lumos_bedrock_app --chat
```

## Available Bedrock Models

Configure in `config/bedrock.yaml`:

```yaml
models:
  bedrock:
    model: "anthropic.claude-3-5-sonnet-20241022-v2:0"  # Default
    # Other options:
    # model: "anthropic.claude-3-haiku-20240307-v1:0"
    # model: "anthropic.claude-3-opus-20240229-v1:0"
```

## Cost Considerations

- Bedrock pricing is pay-per-use (input/output tokens)
- Monitor usage through AWS CloudWatch
- Set up billing alarms for cost control
- Consider using Haiku model for cost optimization

## Production Deployment

### 1. Use IAM Roles (Recommended)

Instead of access keys, use IAM roles for production:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    }
  ]
}
```

### 2. Container Deployment

Create a Dockerfile for Bedrock deployment:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv install

# Set Bedrock as default
ENV ENVIRONMENT=bedrock
ENV AWS_DEFAULT_REGION=us-east-1

EXPOSE 8000
CMD ["uv", "run", "python", "-m", "meccaai.apps.lumos_bedrock_app", "--chat"]
```

### 3. Monitoring and Logging

- Enable AWS CloudTrail for API calls
- Use CloudWatch for monitoring
- Set up alerts for error rates and costs

## Troubleshooting

### Common Issues

1. **Model Access Denied**
   - Check Bedrock model access in AWS console
   - Verify region supports the model

2. **Credential Errors**
   - Verify AWS credentials are correctly configured
   - Check IAM permissions for Bedrock

3. **Timeout Errors**
   - Increase timeout in configuration
   - Check network connectivity to AWS

4. **Cost Concerns**
   - Monitor token usage
   - Switch to cheaper models (Haiku) for testing

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
uv run python -m meccaai.apps.lumos_bedrock_app chat "test message"
```

## Migration from OpenAI

To migrate from OpenAI to Bedrock:

1. Update environment to use `bedrock.yaml` config
2. Switch from `lumos_app` to `lumos_bedrock_app`
3. Update any OpenAI-specific integrations
4. Test all workflows with Bedrock models

The agent interfaces remain the same, so your existing prompts and workflows should work without changes.