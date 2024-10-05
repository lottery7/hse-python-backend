import json
import math

from urllib.parse import parse_qs, urlparse


async def app(scope, receive, send) -> None:
    if scope["method"] != "GET":
        await send_error(404, send)
        return

    path_nodes = urlparse(scope["path"]).path.split("/")
    if len(path_nodes) <= 1:
        await send_error(404, send)
        return

    match path_nodes[1]:
        case "factorial":
            await send_factorial(scope, send)

        case "fibonacci":
            if len(path_nodes) <= 2:
                await send_error(422, send)
                return

            await send_fibonacci(path_nodes[2], send)

        case "mean":
            await send_mean(receive, send)

        case _:
            await send_error(404, send)
            return


async def read_body(receive):
    body = b""
    more_body = True

    while more_body:
        message = await receive()
        body += message.get("body", b"")
        more_body = message.get("more_body", False)

    return body


def parse_floats(string: str):
    if not string.startswith("[") or not string.endswith("]"):
        raise ValueError()

    number_strings = string.strip("[]").replace(" ", "").split(",")

    result = []
    for num_str in number_strings:
        if len(num_str) > 0:
            result.append(float(num_str))

    return result


async def send_response(status, content_type, body, send):
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                ("content-type", content_type),
                ("content-length", str(len(body)).encode()),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


async def send_error(status, send):
    match status:
        case 404:
            await send_response(404, "text/plain", b"Not found", send)

        case 422:
            await send_response(422, "text/plain", b"Unprocessable Entity", send)

        case 400:
            await send_response(400, "text/plain", b"Bad Request", send)

        case _:
            await send_response(500, "text/plain", b"Internal server error", send)


async def send_factorial(scope, send):
    qs = parse_qs(scope["query_string"].decode())

    if "n" not in qs:
        await send_error(422, send)
        return

    n = None
    try:
        n = int(qs["n"][0])
    except:
        await send_error(422, send)
        return

    if n < 0:
        await send_error(400, send)
        return

    result = math.factorial(n)

    await send_response(
        200, "application/json", json.dumps({"result": result}).encode(), send
    )


async def send_fibonacci(unparsed_param, send):
    n = None
    try:
        n = int(unparsed_param)
    except:
        await send_error(422, send)
        return

    if n < 0:
        await send_error(400, send)
        return

    a, b = 0, 1
    for i in range(n):
        a, b = b, a + b

    result = a

    await send_response(
        200, "application/json", json.dumps({"result": result}).encode(), send
    )


async def send_mean(receive, send):
    body = await read_body(receive)
    a = None
    try:
        a = parse_floats(body.decode())
    except:
        await send_error(422, send)
        return

    if len(a) == 0:
        await send_error(400, send)
        return

    result = sum(a) / len(a)

    await send_response(
        200, "application/json", json.dumps({"result": result}).encode(), send
    )
