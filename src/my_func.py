from boto3 import client

from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import parse, ValidationError
from aws_lambda_powertools.utilities.parser.models import S3Model

from urllib.parse import unquote_plus
from zipfile import ZipFile
from io import BytesIO
from pathlib import Path
from os import environ

s3_client = client("s3")


def make_zipped_data(b: bytes, extracted_file_name: str) -> bytes:
    zip_file = BytesIO()
    with ZipFile(zip_file, "w") as z:
        z.writestr(f"{extracted_file_name}", b)

    # 書き込んだ時点で読み込み位置が末尾に移動してしまっているので、先頭に戻す
    zip_file.seek(0)
    return zip_file.read()


def my_handler(event: dict, context: LambdaContext):
    try:
        parsed_event = parse(event=event, model=S3Model)
    except ValidationError as e:
        print(e.json())
        raise e
    # S3Model の型は以下を参照
    # https://github.com/aws-powertools/powertools-lambda-python/blob/d3d94cc38d72bc99d54bb5864420daa73c8f9ac4/aws_lambda_powertools/utilities/parser/models/s3.py#L464
    s3s = [r.s3 for r in parsed_event.Records]
    print(s3s)

    # ウォーム環境での更新漏れを防ぐために、環境変数の読み込みは関数内で行う
    dst_bucket = environ["DST_BUCKET"]

    for s3 in s3s:
        bucket_name = s3.bucket.name

        # S3 イベント中では key は urlencode された状態だが、get_object メソッドで使用する際には元の値である必要がある
        quoted_key = s3.object.key
        key = unquote_plus(quoted_key)
        print(f"{bucket_name=}, {key=}")
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=key)
        body = s3_object["Body"].read()
        print(f"[{bucket_name}/{key}] {len(body)}")

        print(f"make zip archive from {key}")
        # 元の S3 オブジェクトがファイル名に / を含む (疑似的なディレクトリに配置されている) 場合には、
        # ZIP ファイルから展開した場合のファイル名は疑似ディレクトリは含まないようにする
        zipped = make_zipped_data(b=body, extracted_file_name=Path(key).name)
        print(f"zip archive from {key} is made")

        dst_key = f"{key}.zip"
        print(f"upload zip archive (to {dst_bucket=}/{dst_key=})")

        try:
            s3_client.put_object(Bucket=dst_bucket, Key=dst_key, Body=zipped)
        except Exception as e:
            print(f"[ERROR] failed to upload zip file: {e}")
            raise e

        print(f"archive of {bucket_name}/{key} is done.")
