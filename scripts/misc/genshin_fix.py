import asyncio
import logging
import os
import re

import amqcsl
from amqcsl.objects import CSLTrack
from dotenv import load_dotenv
from log import setup_logging

_ = load_dotenv()


async def main(logger: logging.Logger):
    async with amqcsl.AsyncDBClient(
        username=os.getenv('AMQ_USERNAME'),
        password=os.getenv('AMQ_PASSWORD'),
    ) as client:
        matches = await client.iter_tracks(groups=[client.groups['Genshin Impact']], func=process_track)
        for m in matches:
            if m is not None:
                print(m)


async def process_track(client: amqcsl.AsyncDBClient, track: CSLTrack):
    if track.song is None:
        return
    if track.song.name is None:
        return
    if m := re.match(r'([\w\s]+)\s+\((.+)\)', track.song.name):
        return m


if __name__ == '__main__':
    logger = logging.getLogger('INSERT SCRIPT NAME HERE')
    setup_logging()
    asyncio.run(main(logger))
