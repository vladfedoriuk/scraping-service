from django.utils.functional import classproperty

__all__ = ("Scraper",)


class Scraper:
    app_name = "scraper"

    @classproperty
    def scraper_name(cls) -> str:
        return f"{cls.app_name}:{cls.__qualname__.lower()}"

    def __init_subclass__(cls, **kwargs):
        from scraper.scrapers.registry import add_to_registry

        add_to_registry(cls)
        super().__init_subclass__(**kwargs)
