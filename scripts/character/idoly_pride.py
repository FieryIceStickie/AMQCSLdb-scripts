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
    'kotono': 'Kotono Nagase',
    'nagisa': 'Nagisa Ibuki',
    'saki': 'Saki Shiraishi',
    'suzu': 'Suzu Narumiya',
    'mei': 'Mei Hayasaka',
    'sakura': 'Sakura Kawasaki',
    'shizuku': 'Shizuku Hyoudou',
    'chisa': 'Chisa Shiraishi',
    'rei': 'Rei Ichinose',
    'haruko': 'Haruko Saeki',
    'rui': 'Rui Tendou',
    'yuu': 'Yuu Suzumura',
    'sumire': 'Sumire Okuyama',
    'rio': 'Rio Kanzaki',
    'aoi': 'Aoi Igawa',
    'ai': 'Ai Komiyama',
    'kokoro': 'Kokoro Akazaki',
    'mana': 'Mana Nagase',
    'fran': 'fran',
    'kana': 'kana',
    'miho': 'miho',
    'kouhei': 'Kouhei Makino',
    'shinji': 'Shinji Saegusa',
    'kyouichi': 'Kyouichi Asakura',
}
artists: cm.ArtistDict = {
    'Mirai Tachibana': 'kotono',
    'Kokona Natsume': 'nagisa',
    'Koharu Miyazawa': 'saki',
    'Kanata Aikawa': 'suzu',
    'Moka Hinata': 'mei',
    'Mai Kanno': 'sakura',
    'Yukina Shutou': 'shizuku',
    'Kanon Takao': 'chisa',
    'Moeko Yuuki': 'rei',
    'Nao Sasaki': 'haruko',
    'Sora Amamiya': 'rui',
    'Momo Asakura': 'yuu',
    'Shiina Natsukawa': 'sumire',
    'Haruka Tomatsu': 'rio',
    'Ayahi Takagaki': 'aoi',
    'Minako Kotobuki': 'ai',
    'Aki Toyosaki': 'kokoro',
    'Sayaka Kanda': 'mana',
    cm.ArtistName('Lynn', original_name='Lynn'): 'fran',
    'Aimi Tanaka': 'kana',
    'Rie Murakawa': 'miho',
    'Sunny Peace': 'sakura shizuku chisa rei haruko',
    'Tsuki no Tempest': 'kotono nagisa saki suzu mei',
    'TRINITYAiLE': 'rui yuu sumire',
    ('LizNoir', 'Idoly Pride'): 'rio aoi ai kokoro',
    ('LizNoir', 'Idoly Pride (Anime)'): 'rio aoi',
    'IIIX': 'fran kana miho',
    'Hoshimi Production': 'kotono nagisa saki suzu mei sakura shizuku chisa rei haruko',
    'Hoshimi All Stars': 'kotono nagisa saki suzu mei sakura shizuku chisa rei haruko rui yuu sumire rio aoi ai kokoro fran kana miho',
    'Sweet Rouge': 'rui sumire chisa nagisa',
    'SOH-dan': 'saki chisa rei mei',
    'Pajapa!': 'suzu shizuku chisa sumire kokoro',
    'spring battler': 'kouhei shinji kyouichi',
}


async def main(logger: logging.Logger):
    async with amqcsl.AsyncDBClient(
        username=os.getenv('AMQ_USERNAME'),
        password=os.getenv('AMQ_PASSWORD'),
    ) as client:
        artist_to_meta = await cm.make_artist_to_meta(
            client,
            characters,
            artists,
            ['Hoshimi All Stars', 'Hoshimi Production', 'LizNoir', 'IIIX', 'TRINITYAiLE'],
        )
        ip_group = client.groups['IDOLY PRIDE']
        tracks = client.iter_tracks('IDOLY PRIDE Collection Album', groups=[ip_group])
        async with asyncio.TaskGroup() as tg:
            _ = [tg.create_task(process_track(client, track, artist_to_meta)) async for track in tracks]

        if cm.prompt(client.queue):
            await client.commit()


async def process_track(client: amqcsl.AsyncDBClient, track: CSLTrack, artist_to_meta: cm.ArtistToMeta) -> None:
    meta = await client.get_metadata(track)
    cm.queue_character_metadata(client, track, artist_to_meta, meta)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    setup_logging()
    asyncio.run(main(logger))
