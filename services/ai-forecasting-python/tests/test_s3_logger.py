"""Tests for S3 forecast logger wiring and standalone behaviour."""
from unittest.mock import patch, MagicMock

from app.services.forecasting_service import calculate_eta


@patch("app.services.forecasting_service.upload_forecast_log")
@patch("app.services.forecasting_service.predict_speed", return_value=20.0)
@patch("app.services.forecasting_service.calculate_haversine_distance", return_value=10.0)
@patch("app.services.forecasting_service.get_latest_telemetry")
def test_upload_forecast_log_called_on_successful_eta(
    mock_telemetry, mock_distance, mock_speed, mock_upload
):
    """After a successful ETA calculation, upload_forecast_log must be called with the right args."""
    mock_telemetry.return_value = MagicMock(latitude=49.28, longitude=-122.92)

    result = calculate_eta("order-123", 49.23, -123.01, "Express")

    assert result is not None
    assert result["distance_km"] == 10.0
    mock_upload.assert_called_once_with("order-123", 10.0, 30.0, "Express")


@patch("app.services.forecasting_service.upload_forecast_log")
@patch("app.services.forecasting_service.get_latest_telemetry", return_value=None)
def test_upload_not_called_when_no_telemetry(mock_telemetry, mock_upload):
    """When there is no telemetry, calculate_eta returns None and the logger should not fire."""
    result = calculate_eta("order-456", 49.23, -123.01)

    assert result is None
    mock_upload.assert_not_called()


@patch.dict("os.environ", {"S3_LOG_BUCKET": ""}, clear=False)
def test_upload_skipped_when_bucket_not_set():
    """upload_forecast_log returns False without error when S3_LOG_BUCKET is empty."""
    import importlib
    import app.utils.s3_logger as mod
    importlib.reload(mod)

    assert mod.upload_forecast_log("order-789", 5.0, 10.0, "Standard") is False
