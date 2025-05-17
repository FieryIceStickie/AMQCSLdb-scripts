import logging
import os

from dotenv import load_dotenv
from rich.pretty import pprint
from log import setup_logging

import amqcsl
from amqcsl.objects._db_types import NewSong
from amqcsl.workflows.character import prompt

_ = load_dotenv()


def main(logger: logging.Logger):
    with amqcsl.DBClient(
        username=os.getenv('AMQ_USERNAME'),
        password=os.getenv('AMQ_PASSWORD'),
    ) as client:
        for track in client.iter_tracks('UMAMUSUME PRETTY DERBY WINNING LIVE 06', groups=[client.groups['Uma Musume Pretty Derby']]):
            if track.album != 'UMAMUSUME PRETTY DERBY WINNING LIVE 06':
                continue
            pprint(track)
            if not track.name or not track.song:
                pprint(track)
                continue
            if any(map(track.name.endswith, ('Saigo no Shoubu', 'Saigo no Kessen', 'Fanfare', '-kyuu'))):
                client.track_edit(
                    track,
                    song=NewSong(track.name, 'Uma Musume'),
                    queue=True,
                )
            elif track.name.endswith('-') or track.name.endswith(')'):
                continue
            elif track.name != track.song.name:
                pprint(track)
        if prompt(client.queue):
            client.commit()

if __name__ == '__main__':
    logger = logging.getLogger('INSERT SCRIPT NAME HERE')
    setup_logging()
    main(logger)
