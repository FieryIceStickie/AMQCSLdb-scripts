import asyncio
import logging
import os

import amqcsl
from dotenv import load_dotenv

from log import setup_logging

_ = load_dotenv()


async def main(logger: logging.Logger):
    async with amqcsl.AsyncDBClient(
        username=os.getenv('AMQ_USERNAME'),
        password=os.getenv('AMQ_PASSWORD'),
        max_query_size=5000,
    ) as client:
        # clist = await client.create_list('instless', client.lists['YousoroEuphonium'])
        clist = client.lists['instless']
        tracks = client.iter_tracks(active_list=clist)
        await client.list_edit(
            clist,
            remove=[
                track
                async for track in tracks  #
                if track.type in ('Instrumental', 'OffVocal')
            ],
        )


if __name__ == '__main__':
    logger = logging.getLogger('instless')
    setup_logging()
    asyncio.run(main(logger))
