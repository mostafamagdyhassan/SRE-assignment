from prometheus_client import Counter, Histogram, Gauge

scan_requests_total = Counter(
    "scan_requests_total",
    "Total number of scan attempts"
)

scan_failures_total = Counter(
    "scan_failures_total",
    "Total number of failed scans"
)

scan_duration_seconds = Histogram(
    "scan_duration_seconds",
    "Time taken to scan file",
    buckets=(0.5, 1, 2, 3, 5, 8, 13, 21, 34, 55)
)

scan_inflight = Gauge(
    "scan_inflight",
    "Number of scans currently running"
)

sqs_messages_received_total = Counter(
    "sqs_messages_received_total",
    "Total SQS messages received"
)
