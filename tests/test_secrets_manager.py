import json
import os
from unittest.mock import MagicMock, patch

from app.core.secrets_manager import SecretManagerProvider


def test_get_secret_from_env():
    """Tests resolving secrets directly from environment variables."""
    with patch.dict(os.environ, {"TEST_DYNAMIC_KEY": "super_secret_val"}):
        val = SecretManagerProvider.get_secret("TEST_DYNAMIC_KEY")
        assert val == "super_secret_val"


def test_get_secret_default_fallback():
    """Tests default value fallback when secret is not set in environment or AWS."""
    with patch.dict(os.environ, {}, clear=True):
        val = SecretManagerProvider.get_secret("NON_EXISTENT_KEY", default="fallback_default")
        assert val == "fallback_default"


def test_get_secret_aws_secrets_manager_mock():
    """Tests AWS Secrets Manager resolution when AWS_SECRETS_MANAGER_SECRET_ID is configured."""
    fake_secret_json = json.dumps({"PRODUCTION_DB_URL": "postgresql://prod:secret@rds/db"})
    mock_boto = MagicMock()
    mock_client = MagicMock()
    mock_client.get_secret_value.return_value = {"SecretString": fake_secret_json}
    mock_boto.client.return_value = mock_client

    with (
        patch.dict(
            os.environ,
            {
                "AWS_SECRETS_MANAGER_SECRET_ID": "arn:aws:secretsmanager:us-east-1:123456:secret:mysecret"
            },
        ),
        patch.dict("sys.modules", {"boto3": mock_boto}),
    ):
        val = SecretManagerProvider.get_secret("PRODUCTION_DB_URL")
        assert val == "postgresql://prod:secret@rds/db"
