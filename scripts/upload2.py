import asyncio
import logging
import os
from pathlib import Path

import amqcsl
from amqcsl.objects import AlbumTrack, ExtraMetadata, TrackPutArtistCredit
from dotenv import load_dotenv
from rich.pretty import pprint

from log import setup_logging

_ = load_dotenv()


async def main(logger: logging.Logger):
    async with amqcsl.AsyncDBClient(
        username=os.getenv('AMQ_USERNAME'),
        password=os.getenv('AMQ_PASSWORD'),
    ) as client:
        path = Path(
            '~/Desktop/[2025.12.24] ラブライブ！蓮ノ空女学院スクールアイドルクラブ 8thシングル「はじまりの羽音」[FLAC]'
        ).expanduser()
        names: dict[str, Path] = {}
        for f in path.iterdir():
            if f.suffix != '.flac':
                continue
            names[f.name[4:-5]] = f

        hasu = await anext(
            artist
            async for artist in client.iter_artists('Hasunosora Jogakuin')
            if artist.disambiguation == 'Love Live! (105-ki)'
        )
        kokona = await anext(
            artist
            async for artist in client.iter_artists('Kokona Nonaka')  #
            if artist.name == 'Kokona Nonaka'
        )
        pprint(hasu)
        pprint(kokona)
        pprint(names)
        input()

        await client.create_album(
            name='Hasunosora Jogakuin School Idol Club 8th Single "Hajimari no Haneoto"',
            original_name='蓮ノ空女学院スクールアイドルクラブ 8thシングル「はじまりの羽音」',
            year=2025,
            groups=[client.groups['Link! Like! Love Live!']],
            tracks=[
                [
                    AlbumTrack('Hajimari no Haneoto', 'はじまりの羽音', 'Hasunosora Jogakuin School Idol Club'),
                    AlbumTrack(
                        'Charming na Hanataba wo!', 'チャーミングな花束を！', 'Hasunosora Jogakuin School Idol Club'
                    ),
                    AlbumTrack('Runway', 'Runway', 'Kokona Nonaka'),
                    AlbumTrack(
                        'Hajimari no Haneoto (Off Vocal)',
                        'はじまりの羽音 (Off Vocal)',
                        'Hasunosora Jogakuin School Idol Club',
                    ),
                    AlbumTrack(
                        'Charming na Hanataba wo! (Off Vocal)',
                        'チャーミングな花束を！ (Off Vocal)',
                        'Hasunosora Jogakuin School Idol Club',
                    ),
                    AlbumTrack('Runway (Off Vocal)', 'Runway (Off Vocal)', 'Kokona Nonaka'),
                ]
            ],
            queue=True,
        )
        pprint(client.queue)
        input()
        await client.commit()

        tracks = [track async for track in client.iter_tracks('Hasunosora Jogakuin School Idol Club 8th Single "Hajimari no Haneoto"')]
        for track in tracks:
            if track.original_simple_artist == 'Kokona Nonaka':
                await client.track_add_metadata(
                    track,
                    ExtraMetadata(True, 'Character', 'Sayaka Murano'),
                    queue=True,
                )
                await client.track_edit(
                    track,
                    artist_credits=[TrackPutArtistCredit(kokona)],
                    type='OffVocal' if track.name and track.name.endswith('(Off Vocal)') else 'Vocal',
                    queue=True,
                )
            else:
                await client.track_add_metadata(
                    track,
                    ExtraMetadata(True, 'Character', 'Kaho Hinoshita'),
                    ExtraMetadata(True, 'Character', 'Ginko Momose'),
                    ExtraMetadata(True, 'Character', 'Sayaka Murano'),
                    ExtraMetadata(True, 'Character', 'Kosuzu Kachimachi'),
                    ExtraMetadata(True, 'Character', 'Rurino Oosawa'),
                    ExtraMetadata(True, 'Character', 'Hime Anyouji'),
                    ExtraMetadata(True, 'Character', 'Ceras Yanagida Lilienfeld'),
                    ExtraMetadata(True, 'Character', 'Izumi Katsuragi'),
                    queue=True,
                )
                await client.track_edit(
                    track,
                    artist_credits=[TrackPutArtistCredit(hasu)],
                    type='OffVocal' if track.name and track.name.endswith('(Off Vocal)') else 'Vocal',
                    queue=True,
                )
        pprint(client.queue)
        input()
        await client.commit()

        for track in tracks:
            await client.add_audio(track, names[track.original_name], queue=True)
        pprint(client.queue)
        input()
        await client.commit()


if __name__ == '__main__':
    logger = logging.getLogger('INSERT SCRIPT NAME HERE')
    setup_logging()
    asyncio.run(main(logger))
