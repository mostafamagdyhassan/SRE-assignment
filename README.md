# S3 File Scanner Service

This service scans newly uploaded S3 objects using ClamAV and tags each object with:

- `scan-result: OK`
- `scan-result: INFECTED`

The system is event-driven and built to meet the following latency target:


## Architecture Overview

S3 → SQS → Scanner → ClamAV → S3 Tag

- LocalStack provides S3 and SQS.
- S3 bucket emits events on object creation.
- Events are delivered to SQS.
- Scanner service consumes SQS messages.
- Files are downloaded and scanned using `clamdscan`.
- The object is tagged with the result.

The scanner and ClamAV daemon run inside the same container.

---

## How to Run

### 1. Start Services

```bash
docker compose up --build

2. Provision Infrastructure
make provision
3. Run Demo
make demo
The demo will:

Upload one clean file
Upload one EICAR test file
Wait for scanning
Print object tags
Health & Metrics
Health endpoint:
http://localhost:8080/health








✅ Step 1 — Confirm Scanner Started Correctly

In another terminal run:

docker logs -f scanner

You must see something like:

Updating virus database...
Starting clamd...
ClamAV daemon is ready.
Starting metrics server...
Starting scanner worker...


ClamAV daemon is ready.



✅ Step 2 — Test Health Endpoint

Open browser:

http://localhost:8080/health

Expected:

{"status":"ok"}



✅ Step 3 — Test Metrics Endpoint

Open:

http://localhost:8080/metrics

You should see Prometheus-style metrics text output.


✅ Step 4 — Provision S3 and SQS

Now in terminal:

make provision

If you don’t have make installed:

sudo apt install make

After provisioning, verify:

aws --endpoint-url=http://localhost:4566 s3 ls

You should see:

scan-bucket

Then:

aws --endpoint-url=http://localhost:4566 sqs list-queues


✅ Step 5 — Upload Clean File

echo "hello world" > clean.txt
aws --endpoint-url=http://localhost:4566 s3 cp clean.txt s3://scan-bucket/

Now check scanner logs:

docker logs -f scanner

You should see it receive SQS message and scan.

✅ Step 6 — Check Tag
aws --endpoint-url=http://localhost:4566 s3api get-object-tagging \
  --bucket scan-bucket \
  --key clean.txt

Expected:

{
  "TagSet": [
    {
      "Key": "scan-result",
      "Value": "OK"
    }
  ]
}



if:

Containers are running
Health works
Metrics works
Bucket + queue created
Clean file gets scan-result: OK

Then next step is:

🦠 Test Infected Flow (Critical)

This proves ClamAV integration really works.

✅ Step 1 — Upload EICAR File

Make sure you have eicar.com in your project.

Then run:

aws --endpoint-url=http://localhost:4566 s3 cp eicar.com s3://scan-bucket/
✅ Step 2 — Watch Scanner Logs
docker logs -f scanner

You should see:

SQS message received
File downloaded
clamdscan run
Result = INFECTED
Tag written
✅ Step 3 — Verify Tag
aws --endpoint-url=http://localhost:4566 s3api get-object-tagging \
  --bucket scan-bucket \
  --key eicar.com

Expected:

{
  "TagSet": [
    {
      "Key": "scan-result",
      "Value": "INFECTED"
    }
  ]
}

If this works → your malware detection is fully functional.

🔁 After That — Idempotency Test

Upload the same clean file again:

aws --endpoint-url=http://localhost:4566 s3 cp clean.txt s3://scan-bucket/

Scanner should:

Detect tag already exists
Skip scanning
Delete SQS message

If it rescans → bug.

🧵 Final Check — Burst Test

Upload multiple files quickly:

for i in {1..10}; do
  cp clean.txt test$i.txt
  aws --endpoint-url=http://localhost:4566 s3 cp test$i.txt s3://scan-bucket/
done

Check:

http://localhost:8080/metrics

Look at:

scan_requests_total
scan_inflight
