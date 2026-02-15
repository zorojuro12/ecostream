"""
DynamoDB Telemetry Reader Service
Retrieves real-time tracking data from DynamoDB for order delay prediction.
"""
import os
import logging
from typing import Optional
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.api.schemas import Location

logger = logging.getLogger(__name__)

# DynamoDB configuration from environment
DYNAMODB_URL = os.getenv("DYNAMODB_URL", "http://localhost:9000")
REGION = os.getenv("REGION", "us-east-1")
TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "ecostream-telemetry-local")


def get_dynamodb_client():
    """
    Creates and returns a boto3 DynamoDB client.
    When EXECUTION_ENV=lambda, connects to real AWS DynamoDB (no endpoint override).
    Otherwise uses local DynamoDB at DYNAMODB_URL (default http://localhost:9000).
    """
    config = Config(
        region_name=REGION,
        retries={"max_attempts": 3, "mode": "standard"}
    )
    if os.getenv("EXECUTION_ENV") == "lambda":
        # Cloud: use default AWS DynamoDB; credentials from IAM role or env
        return boto3.client("dynamodb", region_name=REGION, config=config)
    # Local: override endpoint and use dummy credentials for DynamoDB Local
    return boto3.client(
        "dynamodb",
        endpoint_url=DYNAMODB_URL,
        region_name=REGION,
        aws_access_key_id="dummy",
        aws_secret_access_key="dummy",
        config=config
    )


def get_latest_telemetry(order_id: str) -> Optional[Location]:
    """
    Retrieves the most recent telemetry data for a given order ID.
    
    Uses DynamoDB Query operation with:
    - Partition Key: orderId = :id
    - ScanIndexForward=False (descending order by timestamp)
    - Limit=1 (only the most recent record)
    
    Args:
        order_id: The order ID to query
        
    Returns:
        Location object if telemetry data is found, None otherwise
    """
    try:
        dynamodb = get_dynamodb_client()
        
        # Query the table for the most recent telemetry record
        response = dynamodb.query(
            TableName=TABLE_NAME,
            KeyConditionExpression="orderId = :id",
            ExpressionAttributeValues={
                ":id": {"S": order_id}
            },
            ScanIndexForward=False,  # Descending order (most recent first)
            Limit=1  # Only get the latest record
        )
        
        # Check if any items were returned
        items = response.get("Items", [])
        if not items:
            logger.debug(f"No telemetry data found for orderId: {order_id}")
            return None
        
        # Extract the first (and only) item
        item = items[0]
        
        # Map DynamoDB response to Location model
        # DynamoDB returns numbers as Decimal, so we convert to float
        latitude = float(item["currentLatitude"]["N"])
        longitude = float(item["currentLongitude"]["N"])
        
        logger.debug(f"Retrieved telemetry for orderId: {order_id}, lat: {latitude}, lng: {longitude}")
        
        return Location(latitude=latitude, longitude=longitude)
        
    except ClientError as e:
        logger.error(f"DynamoDB error retrieving telemetry for orderId {order_id}: {e}")
        return None
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error parsing telemetry data for orderId {order_id}: {e}")
        return None
