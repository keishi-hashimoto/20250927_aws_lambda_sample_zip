import pytest
from pathlib import Path
from my_func import make_zipped_data
from zipfile import ZipFile
from io import BytesIO

THIS_DIR = Path(__file__).parent
SRC_DIR = THIS_DIR / "src"


@pytest.mark.parametrize(
    argnames=["src_file_path"],
    argvalues=[
        pytest.param(SRC_DIR / "sample.txt", id="normal file"),
        pytest.param(SRC_DIR / "japanese_text.txt", id="file with japanese text"),
    ],
)
def test_ok(src_file_path: Path):
    result = make_zipped_data(
        b=src_file_path.read_bytes(),
        extracted_file_name=src_file_path.name,
    )
    file = BytesIO(result)
    # 事前に用意した ZIP ファイルと比較してしまうと、
    # ZIP ファイルそのもののファイル名 (make_zipped_data ではバッファー上に作成しているのでファイル名は None になる)
    # などが差分となり比較に失敗する
    # このため、中身を取り出して比較するようにする
    with ZipFile(file) as z:
        expected = src_file_path.read_bytes()
        # 想定したファイル名で中身が取り出せるか (展開後のファイル名が想定通りになっているか) の確認も兼ねているため、
        # 事前に用意した ZIP ファイルではなく make_zipped_data の結果を用いる
        actual = z.read(src_file_path.name)
        assert expected == actual
