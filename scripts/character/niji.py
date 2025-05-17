import logging
import os

from dotenv import load_dotenv
from log import setup_logging

import amqcsl
from amqcsl.workflows import character as cm

_ = load_dotenv()

characters: cm.CharacterDict = {
    'shioriko': 'Shioriko Mifune',
    'mia': 'Mia Taylor',
    'rina': 'Rina Tennouji',
    'karin': 'Karin Asaka',
    'setsuna': 'Setsuna Yuuki',
    'ai': 'Ai Miyashita',
    'ayumu': 'Ayumu Uehara',
    'kasumi': 'Kasumi Nakasu',
    'shizuku': 'Shizuku Ousaka',
    'kanata': 'Kanata Konoe',
    'emma': 'Emma Verde',
    'lanzhu': 'Lanzhu Zhong',
}

artists: cm.ArtistDict = {
    'Moeka Koizumi': 'shioriko',
    'Shuu Uchida': 'mia',
    'Chiemi Tanaka': 'rina',
    'Miyu Kubota': 'karin',
    'Coco Hayashi': 'setsuna',
    'Natsumi Murakami': 'ai',
    'Aguri Oonishi': 'ayumu',
    'Mayu Sagara': 'kasumi',
    'Kaori Maeda': 'shizuku',
    'Akari Kitou': 'kanata',
    'Maria Sashide': 'emma',
    'Akina Houmoto': 'lanzhu',
    ('Nijigasaki Gakuen School Idol Doukoukai', 'tomori replaced with coco'): 'shioriko mia rina karin setsuna ai ayumu kasumi shizuku kanata emma lanzhu',
}


def main(logger: logging.Logger):
    with amqcsl.DBClient(
        username=os.getenv('AMQ_USERNAME'),
        password=os.getenv('AMQ_PASSWORD'),
    ) as client:
        artist_to_meta = cm.make_artist_to_meta(client, characters, artists, ['Nijigasaki Gakuen'])
        for track in client.iter_tracks('Sazameki no Machikado', batch_size=100):
            if track.artist_credits[0].name in ('Naoki Endou', 'A.L.A.N'):
                continue
            elif track.name and 'Movie Size' in track.name:
                continue
            meta = client.get_metadata(track)
            if (artist := cm.queue_character_metadata(client, track, artist_to_meta, meta)) is not None:
                cm.prompt(track, msg=f'Unidentified artist {artist.name}, continue?', continue_on_empty=True)

        if cm.prompt(client.queue):
            client.commit()


if __name__ == '__main__':
    logger = logging.getLogger('niji')
    setup_logging()
    main(logger)
