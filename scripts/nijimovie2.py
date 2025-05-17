import asyncio
import logging
import os
import re
from pathlib import Path

import amqcsl
import cutlet
from amqcsl.objects import AlbumTrack, TrackPutArtistCredit
from dotenv import load_dotenv
from rich.pretty import pprint

from log import setup_logging

_ = load_dotenv()

storage = Path.cwd() / 'storage'


async def main(logger: logging.Logger):
    cut = cutlet.Cutlet()
    with open(storage / 'nijimovie2.txt', 'r') as file:
        disc1_str, disc2_str = file.read().split('\n\n\n')
    disc1 = [AlbumTrack(cut.romaji(name, title=True), name, '遠藤ナオキ') for name in disc1_str.splitlines()]
    jp_name_to_char_name = {
        '三船栞子': 'Shioriko Mifune',
        'ミア・テイラー': 'Mia Taylor',
        '天王寺璃奈': 'Rina Tennouji',
        '朝香果林': 'Karin Asaka',
        '優木せつ菜': 'Setsuna Yuuki',
        '宮下愛': 'Ai Miyashita',
        '上原歩夢': 'Ayumu Uehara',
        '中須かすみ': 'Kasumi Nakasu',
        '桜坂しずく': 'Shizuku Ousaka',
        '近江彼方': 'Kanata Konoe',
        'エマ・ヴェルデ': 'Emma Verde',
        '鐘嵐珠': 'Lanzhu Zhong',
    }
    name_to_seiyuu = {
        '小泉萌香': 'Moeka Koizumi',
        '内田秀': 'Shuu Uchida',
        '田中ちえ美': 'Chiemi Tanaka',
        '久保田未夢': 'Miyu Kubota',
        '林鼓子': 'Coco Hayashi',
        '村上奈津実': 'Natsumi Murakami',
        '大西亜玖璃': 'Aguri Oonishi',
        '相良茉優': 'Mayu Sagara',
        '前田佳織里': 'Kaori Maeda',
        '鬼頭明里': 'Akari Kitou',
        '指出毬亜': 'Maria Sashide',
        '法元明菜': 'Akina Houmoto',
        'A.L.A.N': 'A.L.A.N',
        '遠藤ナオキ': 'Naoki Endou',
    }
    disc2 = []
    for name_str, artist_str in map(str.splitlines, disc2_str.split('\n\n')):
        name = re.search(r'\((.+) Ver.\)', name_str).group(1)
        artist = re.search(r'\(CV\.(.+)\)', artist_str).group(1)
        disc2.append(
            AlbumTrack(f'Yakusoku ni Nare Bokura no Uta ({jp_name_to_char_name[name]} Ver.)', name_str, artist)
        )

    async with amqcsl.AsyncDBClient(
        username=os.getenv('AMQ_USERNAME'),
        password=os.getenv('AMQ_PASSWORD'),
    ) as client:
        if False:
            await client.create_album(
                name='Eiga "Love Live! Nijigasaki Gakuen School Idol Doukoukai: Kanketsuhen Dai-2-shou" Original Soundtrack & Vocal Collection "Sazameki no Machikado"',
                original_name='映画「ラブライブ！虹ヶ咲学園スクールアイドル同好会 完結編 第2章」オリジナルサウンドトラック&ボーカルコレクション「さざめきの街角」',
                year=2026,
                groups=[client.groups['Love Live! Nijigasaki Gakuen School Idol Doukoukai']],
                tracks=[disc1, disc2],
                queue=True,
            )
            pprint(client.queue)
            input()
            await client.commit()

        if True:
            tracks = client.iter_tracks('Sazameki no Machikado')
            yakusoku = await anext(aiter(client.iter_songs('Yakusoku ni Nare Bokura no Uta')))
            seiyuus = {
                name: await anext(artist async for artist in client.iter_artists(en_name) if artist.name == en_name)
                for name, en_name in name_to_seiyuu.items()
            }

            async for track in tracks:
                assert track.name is not None
                kwargs = {}

                if 'Movie Size' in track.name:
                    name = track.name[:-13]
                    song = await anext(aiter(client.iter_songs(name)))
                    kwargs['song'] = song
                elif 'Yakusoku ni Nare' in track.name:
                    kwargs['song'] = yakusoku
                else:
                    # kwargs['song'] = NewSong(track.name, '遠藤ナオキ')
                    kwargs['song'] = await anext(aiter(client.iter_songs(track.name)))
                    kwargs['type'] = 'Instrumental'

                if track.original_simple_artist in seiyuus:
                    kwargs['artist_credits'] = [TrackPutArtistCredit(seiyuus[track.original_simple_artist])]

                await client.track_edit(track, **kwargs, queue=True) # type: ignore[reportUnknownArgumentType]
            pprint(client.queue)
            input()
            await client.commit()


if __name__ == '__main__':
    logger = logging.getLogger('nijimovie2')
    setup_logging()
    asyncio.run(main(logger))
