import dataclasses
from collections import Callable
from functools import partialmethod

import httpx
import logging

from scraper.utils.client.hooks import log_request, log_response, raise_on_4xx_5xx

logger = logging.getLogger("django")


@dataclasses.dataclass
class HttpClient:
    request_hooks: list[Callable] = dataclasses.field(default_factory=list)
    response_hooks: list[Callable] = dataclasses.field(default_factory=list)
    headers: dict[str, str] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        self.__hooks = self.__collect_event_hooks()

    def __collect_event_hooks(self):
        return {
            "request": [log_request] + self.request_hooks,
            "response": [log_response, raise_on_4xx_5xx] + self.response_hooks,
        }

    def __prepare_client_kwargs(self, client_kwargs=None):
        if client_kwargs is None:
            client_kwargs = {}
        client_kwargs["event_hooks"] = self.__hooks | client_kwargs.get(
            "event_hooks", {}
        )
        return client_kwargs

    def __prepare_request_kwargs(self, request_kwargs=None):
        if request_kwargs is None:
            request_kwargs = {}
        request_kwargs["headers"] = self.headers | request_kwargs.get("headers", {})
        return request_kwargs

    def __make_request(
        self, method: str, url: str, client_kwargs=None, request_kwargs=None
    ):
        client_kwargs = self.__prepare_client_kwargs(client_kwargs)
        request_kwargs = self.__prepare_request_kwargs(request_kwargs)
        with httpx.Client(**client_kwargs) as client:
            try:
                request = client.build_request(method, url, **request_kwargs)
                response = client.send(request)
                return response
            except httpx.RequestError as exc:
                logger.error(f"An error occurred while requesting {exc.request.url!r}.")
            except httpx.HTTPStatusError as exc:
                logger.error(
                    f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."
                )
            return None

    get = partialmethod(__make_request, "GET")
    post = partialmethod(__make_request, "POST")
    put = partialmethod(__make_request, "PUT")
    patch = partialmethod(__make_request, "PATCH")
    delete = partialmethod(__make_request, "DELETE")
