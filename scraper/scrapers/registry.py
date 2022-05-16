from typing import TypeVar, Type

from scraper.scrapers.base import Scraper

__all__ = ("add_to_registry", "get_from_registry", "scraper_choices")

ScraperType = TypeVar("ScraperType", bound=Scraper)

_registry: dict[str, Type[ScraperType]] = {}


def add_to_registry(cls: Type[ScraperType]) -> None:
    scraper_name = cls.scraper_name
    assert (
        scraper_name not in _registry
    ), f"There is already a registered class with {scraper_name=}: {cls}"
    _registry[scraper_name] = cls


def get_from_registry(scraper_name: str) -> Type[ScraperType]:
    assert (
        scraper_name in _registry
    ), f"There is no registered class for {scraper_name=}"
    return _registry[scraper_name]


def scraper_choices() -> tuple[tuple[str, str]]:
    return tuple(
        (scraper_name, str(scraper_cls))
        for scraper_name, scraper_cls in _registry.items()
    )
