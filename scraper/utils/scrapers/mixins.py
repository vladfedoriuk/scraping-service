from typing import TypeVar, Protocol

import httpx
import bs4
from selenium import webdriver
from selenium.webdriver.common.options import BaseOptions
from selenium.webdriver.remote.webdriver import BaseWebDriver

DriverType = TypeVar("DriverType", bound=BaseWebDriver)
DriverOptionsType = TypeVar("DriverOptionsType", bound=BaseOptions)


class ClientMixin:
    @staticmethod
    def get_http_client(*args, **kwargs) -> httpx.Client:
        return httpx.Client(*args, **kwargs)


class BeautifulSoupMixin:
    @staticmethod
    def get_beautiful_soup(*args, **kwargs) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(*args, **kwargs)


class DriverProvider(Protocol[DriverType, DriverOptionsType]):

    def extend_options(self, options: DriverOptionsType):
        pass

    def get_remote_driver(self) -> DriverType:
        ...

    def _get_remote_driver_options(self) -> DriverOptionsType:
        ...


class ChromeDriverProvider(DriverProvider[webdriver.Chrome, webdriver.ChromeOptions]):
    def _get_remote_driver_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.set_capability("browserName", "chrome")
        self.extend_options(options)
        return options

    def get_remote_driver(self):
        from django.conf import settings

        return webdriver.Remote(
            command_executor=settings.SELENIUM_HUB_URL,
            options=self._get_remote_driver_options(),
        )
