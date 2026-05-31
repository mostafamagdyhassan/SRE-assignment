import os

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localstack:4566")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
QUEUE_URL = os.getenv("QUEUE_URL")
SCAN_TMP_DIR = "/tmp/scanner"
MAX_SCAN_TIME = int(os.getenv("MAX_SCAN_TIME", "120"))
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "2"))
