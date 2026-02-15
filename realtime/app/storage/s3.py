# realtime/app/storage/s3.py
import os
import boto3
from botocore.exceptions import NoCredentialsError

def upload_file(local_path: str, s3_path: str, content_type: str = None) -> str:
    bucket = os.getenv("S3_BUCKET", "credit-risk-lake")
    s3 = boto3.client("s3")
    
    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type

    try:
        s3.upload_file(local_path, bucket, s3_path, ExtraArgs=extra_args)
        return f"s3://{bucket}/{s3_path}"
    except NoCredentialsError:
        print("❌ No AWS credentials found.")
        return None
    except Exception as e:
        print(f"❌ Failed to upload to S3: {e}")
        return None
