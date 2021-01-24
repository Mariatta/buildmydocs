import http
import json
import urllib.parse
from typing import Tuple, Type, Union

import uritemplate

JSON_CONTENT_TYPE = "application/json"
UTF_8_CHARSET = "utf-8"
JSON_UTF_8_CHARSET = f"{JSON_CONTENT_TYPE}; charset={UTF_8_CHARSET}"

from webservice.exceptions import BadRequest, HTTPException, ReadthedocsBroken


def create_headers(
    oauth_token,
):

    headers = {}
    if oauth_token is not None:
        headers["authorization"] = f"Token {oauth_token}"
    return headers


def decipher_response(status_code: int, body: bytes):
    if not len(body):
        return None
    decoded_body = body.decode("utf-8")
    data = json.loads(decoded_body)
    if status_code in {200, 201, 204}:
        return data
    else:
        try:
            message = data["message"]
        except (TypeError, KeyError):
            message = None
        exc_type: Type[HTTPException]
        if status_code >= 500:
            exc_type = ReadthedocsBroken
        elif status_code >= 400:
            exc_type = BadRequest
        else:
            exc_type = HTTPException
        status_code_enum = http.HTTPStatus(status_code)
        args: Union[Tuple[http.HTTPStatus, str], Tuple[http.HTTPStatus]]
        if message:
            args = status_code_enum, message
        else:
            args = (status_code_enum,)
        raise exc_type(*args)


DOMAIN = "https://readthedocs.org/api/v3/"


def format_url(url, url_vars, *, base_url=DOMAIN):
    url = urllib.parse.urljoin(base_url, url)
    expanded_url = uritemplate.expand(url, var_dict=url_vars)
    return expanded_url


class ReadthedocsAPI:
    """Work with ReadthedocsAPI"""

    def __init__(
        self,
        session,
        *,
        oauth_token,
        base_url=None,
    ):
        self._session = session
        self.oauth_token = oauth_token
        self.base_url = base_url or DOMAIN

    async def _request(self, method, url, headers, body=b""):
        """Make an HTTP request."""
        async with self._session.request(
            method, url, headers=headers, data=body
        ) as response:
            return response.status, await response.read()

    async def _make_request(
        self,
        method,
        url,
        url_vars,
        data,
    ):
        """Construct and make an HTTP request."""

        filled_url = format_url(url, url_vars, base_url=self.base_url)

        request_headers = create_headers(oauth_token=self.oauth_token)

        if data == b"":
            body = b""
            request_headers["content-length"] = "0"

        else:
            body = json.dumps(data).encode(UTF_8_CHARSET)
            request_headers["content-type"] = JSON_UTF_8_CHARSET
            request_headers["content-length"] = str(len(body))
        response = await self._request(method, filled_url, request_headers, body)
        if not (response[0] == 304):
            data = decipher_response(*response)

        return data

    async def getitem(
        self,
        url,
        url_vars={},
    ):
        """Send a GET request for a single item to the specified endpoint."""

        data, _ = await self._make_request(
            "GET",
            url,
            url_vars,
            b"",
        )
        return data

    async def getiter(
        self,
        url,
        url_vars={},
    ):
        """Return an async iterable for all the items at a specified endpoint."""
        data, more = await self._make_request("GET", url, url_vars, b"")

        if isinstance(data, dict) and "items" in data:
            data = data["items"]

        for item in data:
            yield item
        if more:
            # `yield from` is not supported in coroutines.
            async for item in self.getiter(more, url_vars):
                yield item

    async def post(
        self,
        url,
        url_vars={},
        *,
        data=b"",
    ):
        data = await self._make_request(
            "POST",
            url,
            url_vars,
            data,
        )
        return data

    async def patch(
        self,
        url,
        url_vars={},
        *,
        data=b"",
    ):
        data = await self._make_request("PATCH", url, url_vars, data)
        return data

    async def put(
        self,
        url,
        url_vars={},
        *,
        data=b"",
    ):
        data = await self._make_request("PUT", url, url_vars, data)
        return data

    async def delete(
        self,
        url,
        url_vars={},
        *,
        data=b"",
    ):
        await self._make_request(
            "DELETE",
            url,
            url_vars,
            data,
        )
