.PHONY: up down logs demo provision clean

up:
	docker-compose up -d --build

down:
	docker-compose down

logs:
	docker-compose logs -f scanner

provision:
	aws --endpoint-url=http://localhost:4566 s3 mb s3://scan-bucket
	aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name scan-queue
	aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name scan-dlq

	aws --endpoint-url=http://localhost:4566 s3api put-bucket-notification-configuration \
	--bucket scan-bucket \
	--notification-configuration '{
	  "QueueConfigurations": [{
	    "QueueArn": "arn:aws:sqs:us-east-1:000000000000:scan-queue",
	    "Events": ["s3:ObjectCreated:*"]
	  }]
	}'

demo: up
	sleep 10
	make provision
	aws --endpoint-url=http://localhost:4566 s3 cp testfiles/clean.txt s3://scan-bucket/
	aws --endpoint-url=http://localhost:4566 s3 cp testfiles/eicar.com s3://scan-bucket/
	sleep 5
	aws --endpoint-url=http://localhost:4566 s3api get-object-tagging --bucket scan-bucket --key clean.txt
	aws --endpoint-url=http://localhost:4566 s3api get-object-tagging --bucket scan-bucket --key eicar.com
