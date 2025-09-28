from boto3 import client

from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import parse, ValidationError
from aws_lambda_powertools.utilities.parser.models import S3Model

s3_client = client("s3")


def my_handler(event: dict, context: LambdaContext):
    try:
        parsed_event = parse(event=event, model=S3Model)
    except ValidationError as e:
        print(e.json())
        return
    # S3Model の型は以下を参照
    # https://github.com/aws-powertools/powertools-lambda-python/blob/d3d94cc38d72bc99d54bb5864420daa73c8f9ac4/aws_lambda_powertools/utilities/parser/models/s3.py#L464
    s3s = [r.s3 for r in parsed_event.Records]
    print(s3s)

    # TODO: get source file from s3 bucket
    for s3 in s3s:
        bucket_name = s3.bucket.name
        key = s3.object.key
        print(f"{bucket_name=}, {key=}")
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=key)
        body = s3_object["Body"].read()
        print(f"[{bucket_name}/{key}] {len(body)}")
