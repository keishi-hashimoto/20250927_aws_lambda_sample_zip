import json
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import parse, BaseModel, ValidationError
from pydantic import ConfigDict
from typing import TypedDict


class MyEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: int
    y: int


class Response(TypedDict):
    statusCode: int
    body: str


def my_handler(_event: dict, context: LambdaContext) -> Response:
    try:
        event = parse(event=_event, model=MyEvent)
    except ValidationError as e:
        print(e.json())
        return Response(statusCode=400, body=json.dumps({"error": "BAD REQUEST"}))
    x = event.x
    y = event.y
    body = json.dumps({"result": x / y})
    return Response(statusCode=200, body=body)
