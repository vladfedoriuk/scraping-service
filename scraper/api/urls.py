from rest_framework import routers

from scraper.api.views import ScrapedDataViewSet

router = routers.DefaultRouter()
router.register(r"scraped-data", ScrapedDataViewSet)

urlpatterns = router.urls
