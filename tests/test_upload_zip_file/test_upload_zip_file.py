from my_func import my_handler, s3_client
from zipfile import ZipFile
from io import BytesIO
from pathlib import Path
from moto.core.models import patch_client
from urllib.parse import unquote_plus
from botocore.errorfactory import ClientError

import pytest
from os import environ


def test_ok(patched_client, s3_event, dst_bucket_name, body):
    patch_client(s3_client)
    context = ""
    my_handler(
        s3_event,
        # context は使用しないので適当で良い
        context,  # type: ignore
    )
    src_file_keys = [
        unquote_plus(record["s3"]["object"]["key"]) for record in s3_event["Records"]
    ]

    for src_file_key in src_file_keys:
        # ファイルが存在しているかを見に行く
        result = patched_client.get_object(
            Bucket=dst_bucket_name, Key=f"{src_file_key}.zip"
        )

        zip_file = BytesIO(result["Body"].read())

        with ZipFile(zip_file) as z:
            # メンバーが 1 つのみである
            assert len(z.filelist) == 1

            # 中身が一致している
            assert z.read(Path(src_file_key).name) == body


def test_ng_no_such_bucket(s3_event, dst_bucket_name):
    original = environ["DST_BUCKET"]
    environ["DST_BUCKET"] = f"{dst_bucket_name}dummy"
    try:
        patch_client(s3_client)
        context = ""
        with pytest.raises(ClientError):
            my_handler(
                s3_event,
                # context は使用しないので適当で良い
                context,  # type: ignore
            )
    finally:
        environ["DST_BUCKET"] = original
