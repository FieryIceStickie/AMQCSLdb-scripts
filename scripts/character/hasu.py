import asyncio
import logging
import os

import amqcsl
from amqcsl.objects import CSLTrack
from amqcsl.workflows import character as cm
from dotenv import load_dotenv

from log import setup_logging

_ = load_dotenv()

characters: cm.CharacterDict = {
    'kaho': 'Kaho Hinoshita',
    'kozue': 'Kozue Otomune',
    'ginko': 'Ginko Momose',
    'sayaka': 'Sayaka Murano',
    'tsuzuri': 'Tsuzuri Yuugiri',
    'kosuzu': 'Kosuzu Kachimachi',
    'rurino': 'Rurino Oosawa',
    'megumi': 'Megumi Fujishima',
    'hime': 'Hime Anyouji',
    'ceras': 'Ceras Yanagida Lilienfeld',
    'izumi': 'Izumi Katsuragi',
}
# fmt: off
artists: cm.ArtistDict = {
    'Nozomi Nirei': 'kaho',
    'Niina Hanamiya': 'kozue',
    'Hina Sakurai': 'ginko',
    'Kokona Nonaka': 'sayaka',
    'Kotoko Sasaki': 'tsuzuri',
    'Fuuka Hayama': 'kosuzu',
    'Kanna Kan': 'rurino',
    'Kona Tsukine': 'megumi',
    'Rin Kurusu': 'hime',
    ('Cerise Bouquet', 'Love Live! (103-ki)'): 'kozue kaho',
    ('Cerise Bouquet', 'Love Live! (104-ki)'): 'kozue kaho ginko',
    ('Cerise Bouquet', 'Love Live! (105-ki)'): 'kaho ginko',
    ('DOLLCHESTRA', 'Love Live! (103-ki)'): 'tsuzuri sayaka',
    ('DOLLCHESTRA', 'Love Live! (104-ki)'): 'tsuzuri sayaka kosuzu',
    ('DOLLCHESTRA', 'Love Live! (105-ki)'): 'sayaka kosuzu',
    ('Mira-Cra Park!', 'Love Live! (103-ki)'): 'megumi rurino',
    ('Mira-Cra Park!', 'Love Live! (104-ki)'): 'megumi rurino hime',
    ('Mira-Cra Park!', 'Love Live! (105-ki)'): 'rurino hime',
    'Edel Note': 'ceras izumi',
    'Hasu no Kyuujitsu': 'kozue sayaka',
    'KahoMegu♡Gelato': 'kaho megumi',
    'Rurino to Yukai na Tsuzuri-tachi': 'rurino tsuzuri',
    ('Hasunosora Jogakuin School Idol Club', 'Love Live! (No Rurino + Megumi)'): 'kaho kozue sayaka tsuzuri',
    ('Hasunosora Jogakuin School Idol Club', 'Love Live! (103-ki)'): 'kaho kozue sayaka tsuzuri rurino megumi',
    ('Hasunosora Jogakuin School Idol Club', 'Love Live! (104-ki)'): 'kaho kozue ginko sayaka tsuzuri kosuzu rurino megumi hime',
    ('Hasunosora Jogakuin School Idol Club', 'Love Live! (105-ki)'): 'kaho ginko sayaka kosuzu rurino hime ceras izumi',
    'PRINCEε>ε>': 'kaho ginko hime izumi',
    'Ruri&To': 'sayaka kosuzu rurino ceras',
}
# fmt: on


async def main(logger: logging.Logger):
    async with amqcsl.AsyncDBClient(
        username=os.getenv('AMQ_USERNAME'),
        password=os.getenv('AMQ_PASSWORD'),
    ) as client:
        artist_to_meta = await cm.make_artist_to_meta(
            client,
            characters,
            artists,
            ['Hasunosora', 'Love Live!'],
        )
        my_group = client.groups['Link! Like! Love Live!']
        tracks = client.iter_tracks(groups=[my_group], batch_size=100)
        async with asyncio.TaskGroup() as tg:
            _ = [tg.create_task(process_track(client, track, artist_to_meta)) async for track in tracks]

        if cm.prompt(client.queue):
            await client.commit()


async def process_track(
    client: amqcsl.AsyncDBClient,
    track: CSLTrack,
    artist_to_meta: cm.ArtistToMeta,
) -> None:
    meta = await client.get_metadata(track)
    cm.queue_character_metadata(client, track, artist_to_meta, meta)


if __name__ == '__main__':
    logger = logging.getLogger('test.py')
    setup_logging()
    asyncio.run(main(logger))
