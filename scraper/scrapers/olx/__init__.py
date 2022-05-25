from datetime import timedelta

from scraper.scrapers import Scraper
from scraper.scrapers.olx.mixins import OLXScraperMixin
from scraper.utils.scrapers.mixins import ChromeDriverProvider

__all__ = ("LaptopsOLXScraper",)


class LaptopsOLXScraper(Scraper, ChromeDriverProvider, OLXScraperMixin):
    scrape_data_countdown: timedelta = timedelta(minutes=1)
