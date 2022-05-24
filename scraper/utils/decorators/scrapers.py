from contextlib import contextmanager
from typing import TypeVar

from selenium.webdriver.remote.webdriver import BaseWebDriver

DriverType = TypeVar("DriverType", bound=BaseWebDriver)


@contextmanager
def quiting_driver(driver: DriverType):
    try:
        yield driver
    finally:
        driver.quit()
