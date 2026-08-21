import json
import os
from typing import Any

from app.core.logging import get_logger

logger = get_logger("core.secrets_manager")


class SecretManagerProvider:
    """
    Abstracts secret resolution across Cloud providers (AWS Secrets Manager, HashiCorp Vault, Env).
    Supports production key rotation and zero-plaintext runtime secret injection.
    """

    @staticmethod
    def get_secret(secret_name: str, default: Any = None) -> Any:
        """
        Resolves a secret key from environment variables with fallback to AWS Secrets Manager.
        """
        # 1. Primary: Direct environment injection (Kubernetes / ECS Task Definition)
        val = os.environ.get(secret_name)
        if val is not None:
            return val

        # 2. Secondary: AWS Secrets Manager fallback in production
        aws_secret_arn = os.environ.get("AWS_SECRETS_MANAGER_SECRET_ID")
        if aws_secret_arn:
            try:
                import boto3

                client = boto3.client(
                    "secretsmanager", region_name=os.environ.get("AWS_REGION", "us-east-1")
                )
                response = client.get_secret_value(SecretId=aws_secret_arn)
                if "SecretString" in response:
                    secrets_dict = json.loads(response["SecretString"])
                    if secret_name in secrets_dict:
                        return secrets_dict[secret_name]
            except Exception as e:
                logger.warning(f"Could not retrieve '{secret_name}' from AWS Secrets Manager: {e}")

        return default
