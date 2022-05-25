from typing import cast

import selenium.common
from celery.utils.log import get_task_logger

from scraper.scrapers import Scraper
from scraper.scrapers.base import ScrapeResult
from scraper.utils.decorators.scrapers import quiting_driver
from scraper.utils.scrapers.mixins import DriverProvider
from selenium.webdriver.common.by import By

__all__ = ("OLXScraperMixin",)

logger = get_task_logger(__name__)


class OLXScraperMixin:
    def get_offer_list_url(self) -> str:
        return cast(Scraper, self).state.get("url") or cast(Scraper, self).resource.url

    def scrape(self) -> ScrapeResult:
        with quiting_driver(cast(DriverProvider, self).get_remote_driver()) as driver:
            url = self.get_offer_list_url()
            driver.implicitly_wait(1)
            driver.get(url)
            next_url = driver.find_element(
                by=By.XPATH, value="//a[@data-cy='pagination-forward']"
            ).get_attribute("href")
            offer_divs = driver.find_elements(
                by=By.XPATH, value="//div[@data-cy='l-card']"
            )

            logger.info("OLXScraper: Retrieved offer divs")

            data = []
            for offer_div in offer_divs:
                offer_header = offer_div.find_element(by=By.TAG_NAME, value="h6").text
                offer_link = offer_div.find_element(
                    by=By.TAG_NAME, value="a"
                ).get_attribute("href")
                offer_location = offer_div.find_element(
                    by=By.XPATH, value="//p[@data-testid='location-date']"
                ).text
                data.append(
                    {
                        "header": offer_header,
                        "link": offer_link,
                        "location": offer_location,
                    }
                )
            logger.info("OLXScraper: Parsed header, link, and location.")

            for offer_data in data:
                driver.get(offer_data["link"])
                offer_price = driver.find_element(by=By.XPATH, value="//h3").text
                try:
                    offer_description = driver.find_element(
                        by=By.XPATH,
                        value="//div[@data-cy='ad_description']/div[last()]",
                    ).text
                except selenium.common.exceptions.NoSuchElementException:
                    offer_description = ""
                offer_data["price"] = offer_price
                offer_data["description"] = offer_description

            logger.info("OLXScraper: Parsed price and description")

            scraped_data = cast(Scraper, self).build_scraped_data(data)
            return ScrapeResult(data=scraped_data, state={"url": next_url})
