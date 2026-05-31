import boto3
from config import S3_ENDPOINT, AWS_REGION

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    region_name=AWS_REGION,
    aws_access_key_id="test",
    aws_secret_access_key="test",
)

def download_object(bucket, key, dest):
    s3.download_file(bucket, key, dest)

def tag_object(bucket, key, result):
    s3.put_object_tagging(
        Bucket=bucket,
        Key=key,
        Tagging={
            "TagSet": [
                {"Key": "scan-result", "Value": result}
            ]
        }
    )

def object_already_scanned(bucket, key):
    try:
        tags = s3.get_object_tagging(Bucket=bucket, Key=key)
        for tag in tags["TagSet"]:
            if tag["Key"] == "scan-result":
                return True
        return False
    except:
        return False
