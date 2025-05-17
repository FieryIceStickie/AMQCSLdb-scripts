import asyncio
import logging
import os
import re
from pathlib import Path

import amqcsl
from amqcsl.workflows.character import prompt
from dotenv import load_dotenv
from log import setup_logging

_ = load_dotenv()


async def main(logger: logging.Logger):
    async with amqcsl.AsyncDBClient(
        username=os.getenv('AMQ_USERNAME'),
        password=os.getenv('AMQ_PASSWORD'),
    ) as client:
        tracks = [*await client.iter_tracks('Hollow Knight: Silksong')]
        p = Path(
            '/Users/stickie/Library/Application Support/Steam/steamapps/music/Hollow Knight Silksong - Official Soundtrack/HK_SS_OST_FLAC_V2'
        )
        for path in p.glob('*.flac'):
            match = re.match(r'(\d+) (.+)\.flac', path.name)
            if match is None:
                print(path)
                return
            song_num, song_name = match.groups()
            track = tracks[int(song_num) - 1]
            if track.name != song_name:
                return
            if track.name in ('Clover Dancers', 'Cutting Through'):
                await client.add_audio(track, path, queue=True)
        if prompt(client.queue):
            await client.commit()


if __name__ == '__main__':
    logger = logging.getLogger('INSERT SCRIPT NAME HERE')
    setup_logging()
    asyncio.run(main(logger))
