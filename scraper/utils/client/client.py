import dataclasses
import logging
from collections.abc import Callable
from functools import partialmethod

import httpx

from httpx._types import HeaderTypes

from scraper.utils.client.hooks import log_request, log_response, raise_on_4xx_5xx
from scraper.utils.decorators.misc import with_logger


@dataclasses.dataclass
class HttpClient:
    request_hooks: list[Callable] = dataclasses.field(default_factory=list)
    response_hooks: list[Callable] = dataclasses.field(default_factory=list)
    headers: HeaderTypes = dataclasses.field(default_factory=dict)
    logger: logging.Logger = dataclasses.field(
        default_factory=lambda: logging.getLogger("django")
    )

    def __post_init__(self):
        self.__with_logger = with_logger(self.logger)
        self.__hooks = self.__collect_event_hooks()

    def __collect_event_hooks(self):
        return {
            "request": [self.__with_logger(log_request)] + self.request_hooks,
            "response": [self.__with_logger(log_response)]
            + self.response_hooks
            + [raise_on_4xx_5xx],
        }

    def __prepare_client_kwargs(self, client_kwargs=None):
        client_kwargs = {} if client_kwargs is None else client_kwargs
        client_kwargs["event_hooks"] = self.__hooks | client_kwargs.get(
            "event_hooks", {}
        )
        return client_kwargs

    def __prepare_request_kwargs(self, request_kwargs=None):
        request_kwargs = {} if request_kwargs is None else request_kwargs
        request_kwargs["headers"] = self.headers | request_kwargs.get("headers", {})
        return request_kwargs

    def __make_request(
        self, method: str, url: str, client_kwargs=None, request_kwargs=None
    ):
        client_kwargs = self.__prepare_client_kwargs(client_kwargs)
        request_kwargs = self.__prepare_request_kwargs(request_kwargs)
        with httpx.Client(**client_kwargs) as client:
            try:
                return client.request(method, url, **request_kwargs)
            except httpx.RequestError as exc:
                self.logger.error(
                    f"An error occurred while requesting {exc.request.url!r}."
                )
                self.logger.exception(exc)
            except httpx.HTTPStatusError as exc:
                self.logger.error(
                    f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."
                )
            return None

    get = partialmethod(__make_request, "GET")
    post = partialmethod(__make_request, "POST")
    put = partialmethod(__make_request, "PUT")
    patch = partialmethod(__make_request, "PATCH")
    delete = partialmethod(__make_request, "DELETE")
