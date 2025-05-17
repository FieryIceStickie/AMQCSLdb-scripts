import asyncio
import logging
import os

import amqcsl
from amqcsl.objects import CSLList
from dotenv import load_dotenv
from rich.pretty import pprint

from log import setup_logging

_ = load_dotenv()


async def main(logger: logging.Logger):
    async with amqcsl.AsyncDBClient(
        username=os.getenv('AMQ_USERNAME'),
        password=os.getenv('AMQ_PASSWORD'),
        max_query_size=3500,
    ) as client:
        fake_list = CSLList('019673b7-96cd-76d3-bd9f-0518973785e6', 'learn_cho', 122)
        tracks = [
            (track.name, track.original_simple_artist) async for track in client.iter_tracks(active_list=fake_list)
        ]
        pprint(tracks)


if __name__ == '__main__':
    logger = logging.getLogger('Async')
    setup_logging()
    asyncio.run(main(logger))
