from dataclasses import asdict

from msgspec import Struct

from litestar import post
from litestar.params import FromQuery, JSONBody, RequestBody
from litestar.status_codes import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from litestar.testing import create_test_client

from . import Form


def test_request_body_json() -> None:
    @post(path="/test")
    def test_method(data: JSONBody[Form]) -> None:
        assert isinstance(data, Form)

    with create_test_client(test_method) as client:
        response = client.post("/test", json=asdict(Form(name="Moishe Zuchmir", age=30, programmer=True, value="100")))
        assert response.status_code == HTTP_201_CREATED


def test_request_body_declared_with_request_body() -> None:
    @post(path="/test")
    def test_method(data: RequestBody[Form]) -> None:
        assert isinstance(data, Form)

    with create_test_client(test_method) as client:
        response = client.post("/test", json=asdict(Form(name="Moishe Zuchmir", age=30, programmer=True, value="100")))
        assert response.status_code == HTTP_201_CREATED


def test_empty_dict_allowed() -> None:
    @post(path="/test")
    def test_method(data: JSONBody[dict]) -> None:
        assert isinstance(data, dict)

    with create_test_client(test_method) as client:
        response = client.post("/test", json={})
        assert response.status_code == HTTP_201_CREATED


def test_no_body_without_default() -> None:
    @post(path="/test")
    def test_method(data: JSONBody[dict]) -> None:
        pass

    with create_test_client(test_method) as client:
        response = client.post("/test")

        assert response.status_code == HTTP_400_BAD_REQUEST
        assert response.json()["extra"] == [
            {"message": "Missing required field 'data'", "key": "data", "source": "body"}
        ]


def test_no_body_with_invalid_other_param() -> None:
    @post(path="/test")
    def test_method(limit: FromQuery[int], data: JSONBody[dict | None] = None) -> None:
        pass

    with create_test_client(test_method) as client:
        response = client.post("/test", params={"limit": "not-an-int"})

        assert response.status_code == HTTP_400_BAD_REQUEST
        assert response.json()["extra"] == [
            {"message": "Expected `int`, got `str`", "key": "limit", "source": "query"}
        ]


def test_no_body_with_default() -> None:
    class Test(Struct, frozen=True):
        name: str

    default = Test(name="default")

    @post(path="/test", signature_types=[Test])
    def test_method(data: JSONBody[Test] = default) -> Test:
        return data

    with create_test_client(test_method) as client:
        response = client.post("/test")
        assert response.status_code == HTTP_201_CREATED
        assert response.json() == {"name": "default"}
