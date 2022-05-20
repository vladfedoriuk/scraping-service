import logging

import httpx


def log_request(logger: logging.Logger, request: httpx.Request):
    logger.info(
        f"Request event hook: {request.method} {request.url} - Waiting for response"
    )


def log_response(logger: logging.Logger, response: httpx.Response):
    request = response.request
    logger.info(
        f"Response event hook: {request.method} {request.url} - Status {response.status_code}"
    )


def raise_on_4xx_5xx(response: httpx.Response):
    response.raise_for_status()
