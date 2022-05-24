import time
from collections.abc import Iterable
from functools import partial
from typing import List, Union

import telegram
from fastapi import FastAPI, Depends, BackgroundTasks
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


def send_data_to_telegram(
    bot: telegram.Bot,
    channel_id: str,
    scraped_data: Union[List[ScrapedData], ScrapedData],
):
    scraped_data = (
        scraped_data if isinstance(scraped_data, Iterable) else (scraped_data,)
    )
    for data in scraped_data:
        time.sleep(5)
        bot.send_message(
            chat_id=channel_id, text=data.data, parse_mode=telegram.ParseMode.HTML
        )


@app.post("/telegram-integration-web-hook/")
async def accept_scraped_data(
    scraped_data: Union[List[ScrapedData], ScrapedData],
    background_tasks: BackgroundTasks,
    bot: telegram.Bot = Depends(get_bot),
    channel_id: str = Depends(get_channel_id),
):
    background_tasks.add_task(
        partial(send_data_to_telegram, bot, channel_id), scraped_data
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
