import logging

import httpx


def log_request(request: httpx.Request):
    logger = logging.getLogger("django")
    logger.info(
        f"Request event hook: {request.method} {request.url} - Waiting for response"
    )


def log_response(response: httpx.Response):
    logger = logging.getLogger("django")
    request = response.request
    logger.info(
        f"Response event hook: {request.method} {request.url} - Status {response.status_code}"
    )


def raise_on_4xx_5xx(response: httpx.Response):
    response.raise_for_status()
