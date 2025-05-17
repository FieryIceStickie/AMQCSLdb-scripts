import logging
import os
import re

import amqcsl
from amqcsl.workflows import character as cm
from dotenv import load_dotenv
from log import setup_logging

_ = load_dotenv()

characters: cm.CharacterDict = {
    'kanon': 'Kanon Shibuya',
    'keke': 'Keke Tang',
    'sumire': 'Sumire Heanna',
    'chisato': 'Chisato Arashi',
    'ren': 'Ren Hazuki',
    'kinako': 'Kinako Sakurakouji',
    'natsumi': 'Natsumi Onitsuka',
    'shiki': 'Shiki Wakana',
    'mei': 'Mei Yoneme',
    'margarete': 'Margarete Wien',
    'tomari': 'Tomari Onitsuka',
}

artists: cm.ArtistDict = {
    'Sayuri Date': 'kanon',
    'Liyuu': 'keke',
    'Nako Misaki': 'chisato',
    'Naomi Payton': 'sumire',
    'Nagisa Aoyama': 'ren',
    'Nozomi Suzuhara': 'kinako',
    'Aya Emori': 'natsumi',
    'Wakana Ookuma': 'shiki',
    'Akane Yabushima': 'mei',
    'Yuina': 'margarete',
    'Sakura Sakakura': 'tomari',
}


def main(logger: logging.Logger):
    with amqcsl.DBClient(
        username=os.getenv('AMQ_USERNAME'),
        password=os.getenv('AMQ_PASSWORD'),
    ) as client:
        artist_to_meta = cm.make_artist_to_meta(
            client,
            characters,
            artists,
            ['Liella!'],
        )
        superstar_group = client.groups['Love Live! Superstar!!']
        for track in client.iter_tracks('Solo', groups=[superstar_group]):
            name = track.name
            assert name is not None
            (cred,) = track.artist_credits
            (character,) = artist_to_meta[cred.artist]
            new_name = re.sub(r'\(\w* \w* Solo ver.\)', f'({character.value} Solo Ver.)', name)
            logger.info(f'Changing {name} to {new_name}')
            client.track_edit(track, name=new_name, original_artist=cred.artist.name, queue=True)

        if cm.prompt(client.queue):
            client.commit()


if __name__ == '__main__':
    logger = logging.getLogger(__file__)
    setup_logging()
    main(logger)
