from my_func import my_handler, Response
import pytest
import json
from pydantic import ValidationError


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
    ],
)
def test_success(event: dict, expected: Response):
    assert (
        my_handler(
            event=event,  # type: ignore
            context="",  # type: ignore
        )
        == expected
    )


@pytest.mark.parametrize(
    argnames=["event"],
    argvalues=[
        pytest.param(
            {"x": 10, "y": "hoge"},
            id="invalid type",
        ),
        pytest.param(
            {"x": 10},
            id="missing requrired key",
        ),
        pytest.param(
            {"x": 10, "z": 2},
            id="invalid key",
        ),
        pytest.param(
            {"x": 10, "y": 2, "z": 3},
            id="additional key",
        ),
    ],
)
def test_validation_error(event: dict):
    with pytest.raises(ValidationError):
        my_handler(event=event, context="")  # type: ignore
