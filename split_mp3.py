#!/usr/bin/env python3
"""
uses pydub==0.23.1

"""
import argparse
from pathlib import Path

from pydub import AudioSegment


def run():
    parser = argparse.ArgumentParser(
        description="Splits mp3 files into segments of <seg-minutes> minutes.\n"
                    "If the last segment is shorter than half of <seg-minutes>"
                    "it will be added to the previous segment.")
    parser.add_argument(
        'file',
        help='mp3 filename to split'
    )
    parser.add_argument(
        '--seg-minutes',
        type=int,
        default=10,
        help='length in seconds of each segment'
    )
    parser.add_argument(
        '--overlap_seconds',
        type=int,
        default=1,
        help='start each segement overlap seconds before'
    )
    parser.add_argument(
        '--output-folder',
        type=str,
        required=True,
        help='output folder'
    )
    options = parser.parse_args()
    return split_mp3(**vars(options))


def split_mp3(*, file, seg_minutes, overlap_seconds, output_folder):
    p = Path(file)
    if not p.exists():
        raise ValueError(f'{file} does not exists')
    song = AudioSegment.from_mp3(p)
    len_song = len(song)
    seg_millis = seg_minutes * 60 * 1000
    overlap_milli = overlap_seconds * 1000
    segments = []
    for s in range(0, len_song, seg_millis):
        segments.append((max(s - overlap_milli, 0), min(s + seg_millis, len_song)))

    # if the last segment is shorter than 0.5 of segemnt, add it to the previous one
    if len(segments) > 1 and (segments[-1][1] - segments[-1][1] - overlap_milli) < seg_millis / 2:
        segments[-2] = (segments[-2][0], segments[-1][1])
        segments.pop()

    # create output folder if does not exists
    Path(output_folder).mkdir(exist_ok=True, parents=True)

    for idx, (s, e) in enumerate(segments, start=1):
        # create one second overlap
        part = song[s:e]
        part_name = f'{p.stem}_part_{idx}.mp3'
        part_path = Path(output_folder) / Path(part_name)
        part.export(part_path)
        print(f'Exported {idx}/{len(segments)} {part_path} from {s / 1000}:{e / 1000}')


if __name__ == '__main__':
    run()
