#!/usr/bin/env python3
import boto3
import socket
import time
import os
import logging
import sys
from datetime import datetime, timezone

# --- Validate Required Environment Variables ---
required_vars = {
    "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
    "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
    "TARGETS": os.getenv("TARGETS")
}

missing = [key for key, value in required_vars.items() if not value or not value.strip()]
if missing:
    print(f"ERROR: Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)

# --- Parse TARGETS ---
TARGETS = [ip.strip() for ip in required_vars["TARGETS"].split(",") if ip.strip()]
if not TARGETS:
    print("ERROR: TARGETS is set but contains no valid IP addresses.", file=sys.stderr)
    sys.exit(1)

# --- Configuration ---
LOG_FILE = os.path.join(os.path.dirname(__file__), "latency_monitor.log")
MAX_LOG_SIZE = 1 * 1024 * 1024  # 1MB
PORT = 80
TIMEOUT = 1.0  # seconds

# --- CloudWatch Client ---
cloudwatch = boto3.client(
    'cloudwatch', 
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)
                            
# --- Logging Setup ---
def setup_logger():

    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
        with open(LOG_FILE, 'w'):  # Truncate file
            pass

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, mode='a'),
            logging.StreamHandler(sys.stdout)
        ]
    )

setup_logger()
logger = logging.getLogger(__name__)

# --- Latency Function ---
def get_latency(ip, port=80, timeout=1.0):
    try:
        start = time.time()
        with socket.create_connection((ip, port), timeout=timeout):
            end = time.time()
            latency_ms = (end - start) * 1000
            return round(latency_ms, 2)
    except (socket.timeout, socket.error) as e:
        logger.warning(f"Connection to {ip}:{port} failed: {e}")
        return None

# --- Collect and Push Metrics ---
def push_latency_metrics():
    metric_data = []
    timestamp = datetime.now(timezone.utc)

    for ip in TARGETS:
        latency = get_latency(ip, port=PORT, timeout=TIMEOUT)
        if latency is not None:
            logger.info(f"Latency to {ip}:{PORT} = {latency} ms")
            metric_data.append({
                'MetricName': 'RequestLatency',
                'Dimensions': [{'Name': 'TargetIP', 'Value': ip}],
                'Timestamp': timestamp,
                'Value': latency,
                'Unit': 'Milliseconds'
            })

    if metric_data:
        try:
            cloudwatch.put_metric_data(
                Namespace=os.getenv("NAMESPACE", "LatencyMonitor"),
                MetricData=metric_data
            )
            logger.info("Metrics successfully pushed to CloudWatch.")
        except Exception as e:
            logger.error(f"Failed to push metrics to CloudWatch: {e}")
    else:
        logger.warning("No successful latency metrics to push.")

# --- Run ---
if __name__ == "__main__":
    push_latency_metrics()
