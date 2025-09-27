import json
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import BaseModel, event_parser
from pydantic import ConfigDict
from typing import TypedDict


class MyEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: int
    y: int


class Response(TypedDict):
    statusCode: int
    body: str


@event_parser(model=MyEvent)
def my_handler(event: MyEvent, context: LambdaContext) -> Response:
    x = event.x
    y = event.y
    body = json.dumps({"result": x / y})
    return Response(statusCode=200, body=body)
