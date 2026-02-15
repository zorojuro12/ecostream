"""
S3 logging utility for delivery/forecast logs.
Uploads a JSON summary of an AI forecast to an S3 bucket (e.g. for CloudWatch or analytics).
"""
import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

S3_LOG_BUCKET = os.getenv("S3_LOG_BUCKET")
S3_LOG_PREFIX = os.getenv("S3_LOG_PREFIX", "delivery-logs/forecasts")


def upload_forecast_log(
    order_id: str,
    distance_km: float,
    estimated_arrival_minutes: float,
    priority: Optional[str] = None,
) -> bool:
    """
    Upload a JSON summary of an AI forecast to the configured S3 bucket.

    Summary includes order_id, distance_km, estimated_arrival_minutes, optional priority,
    and a timestamp. No-op if S3_LOG_BUCKET is not set.

    Args:
        order_id: Order identifier.
        distance_km: Forecasted distance in km.
        estimated_arrival_minutes: Forecasted ETA in minutes.
        priority: Optional priority (e.g. "Express", "Standard").

    Returns:
        True if upload succeeded, False if bucket not configured or upload failed.
    """
    if not S3_LOG_BUCKET:
        logger.debug("S3_LOG_BUCKET not set; skipping forecast log upload")
        return False

    payload = {
        "order_id": order_id,
        "distance_km": round(distance_km, 2),
        "estimated_arrival_minutes": round(estimated_arrival_minutes, 2),
        "priority": priority,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    key = f"{S3_LOG_PREFIX.rstrip('/')}/{order_id}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"

    try:
        client = boto3.client("s3")
        client.put_object(
            Bucket=S3_LOG_BUCKET,
            Key=key,
            Body=json.dumps(payload, indent=2),
            ContentType="application/json",
        )
        logger.info("Uploaded forecast log to s3://%s/%s", S3_LOG_BUCKET, key)
        return True
    except ClientError as e:
        logger.warning("Failed to upload forecast log to S3: %s", e)
        return False
