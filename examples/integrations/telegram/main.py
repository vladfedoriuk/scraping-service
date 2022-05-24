from typing import List, Union, Iterable

import telegram
from fastapi import FastAPI, Depends
from starlette import status
from starlette.responses import Response

from models import ScrapedData
from settings import Settings, get_settings

app = FastAPI()


def get_bot(settings: Settings = Depends(get_settings)):
    bot_token = settings.telegram_bot_token
    return telegram.Bot(token=bot_token)


def get_channel_id(settings: Settings = Depends(get_settings)):
    channel_name = settings.channel_name
    return f"@{channel_name}"


@app.post("/telegram-integration-web-hook/")
async def accept_scraped_data(
    scraped_data: Union[List[ScrapedData], ScrapedData],
    bot: telegram.Bot = Depends(get_bot),
    channel_id: str = Depends(get_channel_id),
):
    scraped_data = (
        scraped_data if isinstance(scraped_data, Iterable) else (scraped_data,)
    )
    for data in scraped_data:
        bot.send_message(
            chat_id=channel_id, text=data.data, parse_mode=telegram.ParseMode.HTML
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
