from my_func import my_handler, Response
import pytest
import json


@pytest.mark.parametrize(
    argnames=["event", "expected"],
    argvalues=[
        pytest.param(
            {"x": 10, "y": 2},
            Response(statusCode=200, body=json.dumps({"result": 5.0})),
            id="no mod",
        ),
        pytest.param(
            {"x": 10, "y": 4},
            Response(statusCode=200, body=json.dumps({"result": 2.5})),
            id="with mod",
        ),
        pytest.param(
            {"x": 10, "y": "hoge"},
            Response(statusCode=400, body=json.dumps({"error": "BAD REQUEST"})),
            id="invalid type",
        ),
        pytest.param(
            {"x": 10},
            Response(statusCode=400, body=json.dumps({"error": "BAD REQUEST"})),
            id="missing requrired key",
        ),
        pytest.param(
            {"x": 10, "z": 2},
            Response(statusCode=400, body=json.dumps({"error": "BAD REQUEST"})),
            id="invalid key",
        ),
        pytest.param(
            {"x": 10, "y": 2, "z": 3},
            Response(statusCode=400, body=json.dumps({"error": "BAD REQUEST"})),
            id="additional key",
        ),
    ],
)
def test_main(event: dict, expected: Response):
    assert (
        my_handler(
            _event=event,
            context="",  # type: ignore
        )
        == expected
    )
