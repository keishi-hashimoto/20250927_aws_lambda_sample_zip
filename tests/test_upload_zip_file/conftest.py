from pytest import fixture
from moto import mock_aws
from moto.core.models import patch_client
from my_func import s3_client
from os import environ
from pathlib import Path
from jinja2 import Environment
import json
from urllib.parse import quote_plus

RECORD_TEMPLATE_PATH = Path(__file__).parent / "s3_event_record.json"


@fixture(scope="session")
def mock_start():
    with mock_aws():
        yield


@fixture(scope="session")
def patched_client(mock_start):
    patch_client(s3_client)
    return s3_client


@fixture(scope="session")
def src_bucket_name(patched_client):
    bucket_name = environ["DST_BUCKET"]
    patched_client.create_bucket(Bucket=bucket_name)

    return bucket_name


@fixture(scope="session")
def body():
    return b"Hello world"


@fixture(
    scope="session",
    params=[
        ["sample.txt"],
        ["test.txt"],  # dst_bucket にも既に存在しているファイル
        ["hoge/fuga.txt"],  # / を含む key
        ["hoge+fuga.txt"],  # + を含む key
        ["a.txt", "b.txt"],
    ],
    ids=[
        "normal case",
        "dst file is already exists",
        "key contains `/`",
        "key contains `+`",
        "multiple files",
    ],
)
def src_file_keys(patched_client, src_bucket_name, request, body):
    keys = request.param
    for key in keys:
        patched_client.put_object(Bucket=src_bucket_name, Key=key, Body=body)

    return keys


@fixture(scope="session")
def s3_event(src_bucket_name, src_file_keys):
    template = Environment().from_string(source=RECORD_TEMPLATE_PATH.read_text())
    records = [
        json.loads(
            template.render(
                src_bucket_name=src_bucket_name,
                # イベント中ではオブジェクトキーは urlencode されている
                src_file_key=quote_plus(src_file_key),
            )
        )
        for src_file_key in src_file_keys
    ]
    return {"Records": records}


@fixture(scope="session")
def dst_bucket_name(patched_client):
    bucket_name = environ["DST_BUCKET"]
    patched_client.create_bucket(Bucket=bucket_name)

    return bucket_name


@fixture(scope="session")
def existing_key(patched_s3_client, dst_bucket_name):
    key = "test.txt"
    patched_s3_client.put_object(
        Bucket=dst_bucket_name, Key=key, Body="これはテストです"
    )

    return key
