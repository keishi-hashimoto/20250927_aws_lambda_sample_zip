from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import S3Event
from aws_lambda_powertools.utilities.parser import event_parser


@event_parser(model=S3Event)
def my_handler(event: S3Event, context: LambdaContext):
    # S3 イベントの型は以下を参照
    # https://github.com/aws-powertools/powertools-lambda-python/blob/d3d94cc38d72bc99d54bb5864420daa73c8f9ac4/aws_lambda_powertools/utilities/data_classes/s3_event.py#L301
    s3s = [r.s3 for r in event.records]
    print(s3s)

    # TODO: get source file from s3 bucket
    for s3 in s3s:
        print(f"bucket={s3.bucket.name}, key={s3.get_object.key}")
