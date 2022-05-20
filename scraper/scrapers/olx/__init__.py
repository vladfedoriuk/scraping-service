from scraper.scrapers import Scraper
from scraper.scrapers.base import ScrapeResult
from scraper.utils.scrapers.mixins import (
    ChromeDriverProvider,
    ClientMixin,
    BeautifulSoupMixin,
)

__all__ = ("OLXScraper",)


class OLXScraper(Scraper, ChromeDriverProvider, ClientMixin, BeautifulSoupMixin):
    def scrape(self):
        driver = self.get_remote_driver()
        url = self.resource.url
        driver.get(url)
        driver.quit()
        scraped_data = self.build_scraped_data({})
        return ScrapeResult(data=scraped_data, state={})
