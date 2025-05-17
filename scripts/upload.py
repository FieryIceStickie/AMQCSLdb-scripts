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
            '~/Desktop/[2025.12.24] NIJIGAKU Monthly Songs♪12月度シングル「Bravo!」／鐘嵐珠(CV.法元明菜) [FLAC]'
        ).expanduser()
        names: dict[str, Path] = {}
        for f in path.iterdir():
            if f.suffix != '.flac':
                continue
            names[f.name[4:-5]] = f
        akina_houmoto = await anext(
            artist
            async for artist in client.iter_artists('Akina Houmoto')  #
            if artist.name == 'Akina Houmoto'
        )
        pprint(akina_houmoto)
        input()

        await client.create_album(
            name='NIJIGAKU Monthly Songs♪Jyuunigatsu-do Single "Bravo!"',
            original_name='NIJIGAKU Monthly Songs♪12月度シングル「Bravo!」',
            year=2025,
            groups=[client.groups['Love Live! Nijigasaki Gakuen School Idol Doukoukai']],
            tracks=[
                [
                    AlbumTrack('Bravo!', 'Bravo!', 'Akina Houmoto'),
                    AlbumTrack('Seabird', 'Seabird', 'Akina Houmoto'),
                    AlbumTrack('Bravo! (Off Vocal)', 'Bravo! (Off Vocal)', 'Akina Houmoto'),
                    AlbumTrack('Seabird (Off Vocal)', 'Seabird (Off Vocal)', 'Akina Houmoto'),
                ]
            ],
            queue=True,
        )
        pprint(client.queue)
        input()
        await client.commit()

        tracks = [track async for track in client.iter_tracks('NIJIGAKU Monthly Songs♪Jyuunigatsu-do Single "Bravo!"')]
        for track in tracks:
            name = track.name
            if name is None:
                print(track)
                continue
            await client.track_add_metadata(
                track,
                ExtraMetadata(True, 'Character', 'Lanzhu Zhong'),
                queue=True,
            )
            await client.track_edit(
                track,
                artist_credits=[TrackPutArtistCredit(akina_houmoto)],
                type='OffVocal' if name.endswith('(Off Vocal)') else 'Vocal',
                queue=True,
            )
        pprint(client.queue)
        input()
        await client.commit()

        for track in tracks:
            name = track.name
            if name is None:
                print(track)
                continue
            await client.add_audio(track, names[name], queue=True)
        pprint(client.queue)
        input()
        await client.commit()


if __name__ == '__main__':
    logger = logging.getLogger('INSERT SCRIPT NAME HERE')
    setup_logging()
    asyncio.run(main(logger))
