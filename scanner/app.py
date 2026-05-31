import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from sqs_service import receive_messages, delete_message
from s3_service import download_object, tag_object, object_already_scanned
from clamav_service import scan_file
from metrics import scan_requests_total, scan_inflight, sqs_messages_received_total
from config import WORKER_CONCURRENCY

TMP_DIR = "/tmp/scanner"
os.makedirs(TMP_DIR, exist_ok=True)

def process_message(message):
    try:
        body = json.loads(message["Body"])
        record = body["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        if object_already_scanned(bucket, key):
            delete_message(message["ReceiptHandle"])
            return

        scan_requests_total.inc()
        scan_inflight.inc()

        local_path = os.path.join(TMP_DIR, key.replace("/", "_"))

        download_object(bucket, key, local_path)
        result = scan_file(local_path)
        tag_object(bucket, key, result)

        delete_message(message["ReceiptHandle"])

    except Exception as e:
        print(f"Error processing message: {e}")
        # Do NOT delete message → retry

    finally:
        try:
            if os.path.exists(local_path):
                os.remove(local_path)
        except:
            pass
        scan_inflight.dec()
    with ThreadPoolExecutor(max_workers=WORKER_CONCURRENCY) as executor:
        while True:
            messages = receive_messages()
            for message in messages:
                sqs_messages_received_total.inc()
                executor.submit(process_message, message)

if __name__ == "__main__":
    worker_loop()
