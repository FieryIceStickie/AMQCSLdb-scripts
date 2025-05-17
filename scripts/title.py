import asyncio
import logging
import os

from rich.pretty import pprint
import amqcsl
import cutlet
from dotenv import load_dotenv
from log import setup_logging

_ = load_dotenv()


async def main(logger: logging.Logger):
    cut = cutlet.Cutlet()
    async with amqcsl.AsyncDBClient(
        username=os.getenv('AMQ_USERNAME'),
        password=os.getenv('AMQ_PASSWORD'),
        max_query_size=3500,
    ) as client:
        async for track in client.iter_tracks('Atelier Lulua'):
            if track.name is not None:
                continue
            name = cut.romaji(track.original_name, title=True)
            inp = input(f'{track.original_name} -> {name}\n')
            if inp == 'y':
                await client.track_edit(track, name=name, queue=True)

        pprint(client.queue)
        input()
        await client.commit()

if __name__ == '__main__':
    logger = logging.getLogger('title')
    setup_logging()
    asyncio.run(main(logger))
