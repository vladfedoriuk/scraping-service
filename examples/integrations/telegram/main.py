from typing import List, Union

from fastapi import FastAPI, Depends
from models import ScrapedData
from settings import Settings, get_settings

app = FastAPI()


@app.post("/telegram-integration-web-hook/")
async def accept_scraped_data(
    scraped_data: Union[List[ScrapedData], ScrapedData],
    settings: Settings = Depends(get_settings),
):
    print(scraped_data)
    return scraped_data
