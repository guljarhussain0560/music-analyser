from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


def test_sentry_error_tracking_dispatch():
    """Tests that unhandled exceptions are captured by Sentry when SENTRY_DSN is configured."""
    with patch("sentry_sdk.capture_exception") as mock_capture:
        settings.SENTRY_DSN = "https://mockpublickey@sentry.io/123456"

        @app.get("/api/test-simulated-error")
        def route_with_error():
            raise RuntimeError("Simulated unhandled pipeline crash")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-simulated-error")

        assert response.status_code == 500
        assert mock_capture.called, "sentry_sdk.capture_exception must be called on 500 exceptions"

        settings.SENTRY_DSN = None
