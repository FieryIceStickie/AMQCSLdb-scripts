import logging
import os

import amqcsl
from amqcsl.workflows import character as cm
from dotenv import load_dotenv
from log import setup_logging

_ = load_dotenv()

characters: cm.CharacterDict = {
    'kokona': 'Kokona Ootori',
    'shizuka': 'Shizuka',
    'kathrina': 'Kathrina Griebel',
    'yae': 'Yae Niizuma',
    'panda': 'Panda Yanagiba',
    'sasuga': 'Sasuga Chisa',
    'ramona': 'Ramona Wolf',
    'koyomi': 'Koyomi Senju',
    'wang': 'Wang Xue',
    'hikari': 'Hikari Yonaguni',
    'lilja': 'Lilja Kurtbay',
    'kamira': 'Kamira Akiru',
    'iroha': 'Iroha Senju',
    'tsubomi': 'Tsubomi Nekoashi',
    'towa': 'Towa Motosu',
    'mito': 'Mito Shiromaru',
    'yorozu': 'Yorozu Iruru',
    'daikoku': 'Daikoku Karasumori',
    'shigure': 'Shigure Fudeshima',
    'nikako': 'Nikako Toneri',
    'hatsumi': 'Hatsumi Renjakuno',
    'noa': 'Noa Hiiragi',
}

artists: cm.ArtistDict = {
    ('Sirius', 'World Dai Star'): 'kokona shizuka kathrina yae panda sasuga',
    'Manaka Iwami': 'kokona',
    'Ikumi Hasegawa': 'shizuka',
    'Sally Amaki': 'kathrina',
    'Maria Naganawa': 'yae',
    'Naomi Oozora': 'panda',
    'Rico Sasaki': 'sasuga',
    ('Gingaza', 'World Dai Star'): 'ramona koyomi wang hikari lilja',
    'Minami Tanaka': 'ramona',
    'Mariko Toribe': 'koyomi',
    'Miharu Hanai': 'wang',
    'Shino Shimoji': 'hikari',
    'Yukari Anzai': 'lilja',
    ('Gekidan Denki', 'World Dai Star'): 'kamira iroha tsubomi towa mito',
    'Yuuki Wakai': 'kamira',
    'Miho Okasaki': 'iroha',
    'Yuu Serizawa': 'tsubomi',
    'Hikaru Akao': 'towa',
    'Reina Kondou': 'mito',
    ('Eden', 'World Dai Star'): 'yorozu daikoku shigure nikako hatsumi',
    'Hibiku Yamamura': 'yorozu',
    'Lynn': 'daikoku',
    'Maya Yoshioka': 'shigure',
    'Shuka Saitou': 'nikako',
    'Kana Aoi': 'hatsumi',
    'Nanako Mori': 'noa',
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
            ['Sirius', 'Gingaza', 'Gekidan Denki', 'Eden', 'Nanako Mori'],
        )
        wds_group = client.groups['World Dai Star']
        for track in client.iter_tracks(groups=[wds_group]):
            meta = client.get_metadata(track)
            if (artist := cm.queue_character_metadata(client, track, artist_to_meta, meta)) is not None:
                cm.prompt(track, msg=f'Unidentified artist {artist.name}, continue?')

        if cm.prompt(client.queue):
            client.commit()


if __name__ == '__main__':
    logger = logging.getLogger(__file__)
    setup_logging()
    main(logger)
