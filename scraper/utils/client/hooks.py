from scraper.utils.client.client import logger


def log_request(request):
    logger.info(
        f"Request event hook: {request.method} {request.url} - Waiting for response"
    )


def log_response(response):
    request = response.request
    logger.info(
        f"Response event hook: {request.method} {request.url} - Status {response.status_code}"
    )


def raise_on_4xx_5xx(response):
    response.raise_for_status()
