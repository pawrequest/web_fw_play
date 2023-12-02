from abc import ABC
from dataclasses import dataclass
from typing import Mapping


@dataclass
class MediaDict(ABC):
    sp_record: Mapping

    def __post_init__(self):
        self.name = self.sp_record['name']
        self.id = self.sp_record['id']
        self.url = self.sp_record['external_urls']['spotify']


class ReleaseDict(MediaDict):
    def __post_init__(self):
        super().__post_init__()
        self.release_date_precision = self.sp_record['release_date_precision']
        self.release_date = self.sp_record['release_date']

        self.artist = self.sp_record['artists'][0]['name']
        self.artist_id = self.sp_record['artists'][0]['id']

        self.album_group = self.sp_record['album_group']
        self.album_type = self.sp_record['album_type']


class TrackDict(MediaDict):
    def __post_init__(self):
        super().__post_init__()
        self.artist = self.sp_record['artists'][0]['name']
        self.artist_id = self.sp_record['artists'][0]['id']


class ArtistDict(MediaDict):
    def __post_init__(self):
        super().__post_init__()
