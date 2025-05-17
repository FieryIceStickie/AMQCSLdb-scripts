import asyncio
import logging
import os

import amqcsl
from amqcsl.objects import CSLTrack
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
        (*groups,) = map(
            client.groups.__getitem__,
            [
                'Link! Like! Love Live!',
                'Love Live! Nijigasaki Gakuen School Idol Doukoukai',
                'Love Live! School Idol Project',
                'Love Live! Sunshine!!',
                'Love Live! Superstar!!',
                'IKIZULIVE! LOVELIVE! BLUEBIRD',
            ],
        )
        async with asyncio.TaskGroup() as tg:
            _ = [tg.create_task(process_track(client, track)) async for track in client.iter_tracks(groups=groups)]
        pprint(client.queue)
        pprint(no_metas)
        input()
        await client.commit()

no_metas: list[CSLTrack] = []

async def process_track(client: amqcsl.AsyncDBClient, track: CSLTrack):
    if track.type != 'OffVocal':
        return
    meta = await client.get_metadata(track)
    if not meta:
        no_metas.append(track)
        return
    for m in meta.extra_metas:
        if m.key == 'Character':
            await client.track_remove_metadata(track, m, queue=True)



if __name__ == '__main__':
    logger = logging.getLogger('INSERT SCRIPT NAME HERE')
    setup_logging()
    asyncio.run(main(logger))
