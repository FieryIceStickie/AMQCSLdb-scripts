import asyncio
import logging
import os

from dotenv import load_dotenv
from amqcsl.objects._db_types import CSLTrack, ExtraMetadata, NewSong, TrackPutArtistCredit
from log import setup_logging
from rich.pretty import pprint
from amqcsl.workflows.character import prompt

import amqcsl

_ = load_dotenv()

artist = None

async def main(logger: logging.Logger):
    global artist
    async with amqcsl.AsyncDBClient(
        username=os.getenv('AMQ_USERNAME'),
        password=os.getenv('AMQ_PASSWORD'),
    ) as client:
        artist = next(iter(await client.iter_artists('Christopher Larkin')))
        pprint(artist)
        await client.iter_tracks('Hollow Knight: Silksong', func=process_track)
        if prompt(client.queue):
            await client.commit()

async def process_track(client: amqcsl.AsyncDBClient, track: CSLTrack):
    if artist is None:
        return
    await client.track_edit(
        track,
        name=track.original_name,
        song=NewSong(track.original_name, 'Hollow Knight: Silksong'),
        original_artist='Christopher Larkin',
        type='Instrumental',
        groups=[client.groups['Hollow Knight']],
        artist_credits=[TrackPutArtistCredit(artist)],
        queue=True,
    )
    await client.track_add_metadata(track, ExtraMetadata(False, 'Game', 'Hollow Knight: Silksong'), queue=True)

if __name__ == '__main__':
    logger = logging.getLogger('INSERT SCRIPT NAME HERE')
    setup_logging()
    asyncio.run(main(logger))
