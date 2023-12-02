from typing import Any, Dict, Optional

from sqlmodel import Column, Field, JSON, SQLModel


class Media_(SQLModel, table=True):
    id_anid: Optional[int] = Field(default=None, primary_key=True)
    name:str
    # sp_record: Dict = Field(default={}, sa_column=Column(JSON))

    # autofilled by init_fields
    # id: Optional[str] = Field(default=None)
    # name: Optional[str] = Field(default=None)
    # href: Optional[str] = Field(default=None)
    # uri: Optional[str] = Field(default=None)
    # external_urls: Optional[Dict] = Field(default={}, sa_column=Column(JSON))

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        # self.init_fields(self.sp_record)

    # def init_fields(self, data: Dict[str, Any]) -> None:
    #     for attr in self.__annotations__:
    #         if attr != 'sp_record':
    #             value = data.get(attr, None)
    #             setattr(self, attr, value)

    # def init_fields(self, data: Dict[str, Any]) -> None:
    #     for attr in self.__annotations__:
    #         if attr in data and attr != 'sp_record':
    #             setattr(self, attr, data[attr])
    # [setattr(self, attr, data[attr])
    #  for attr in self.__annotations__
    #  if attr in data and attr != 'sp_record']


class Release_(Media_):
    ...
    # release_date_precision: Optional[str] = Field(default=None)
    # release_date: Optional[str] = Field(default=None)
    # album_group: Optional[str] = Field(default=None)
    # album_type: Optional[str] = Field(default=None)
    # artistsartists: Optional[Dict] = Field(default={}, sa_column=Column(JSON))


class Artist_(Media_):
    ...


class Playlist_(Media_):
    ...

# from abc import ABC
# from dataclasses import dataclass
# from typing import Mapping
#
# from pawspot.pawspot_funcs.spot_funcs import _imprecise_date
#
# im
#
#
# @dataclass
# class Media_(ABC):
#     sp_record: Mapping
#
#     def __post_init__(self):
#         self.name = self.sp_record['name']
#         self.id = self.sp_record['id']
#         self.url = self.sp_record['external_urls']['spotify']
#
#
# class Release_(Media_):
#     def __post_init__(self):
#         super().__post_init__()
#         release_date_precision = self.sp_record['release_date_precision']
#         release_date = _imprecise_date(self.sp_record['release_date'],
#                                        release_date_precision)  # convert date string to datetime obj, insert spurious 1s if precision < day
#         self.artist = self.sp_record['artists'][0]['name']
#         self.artist_id = self.sp_record['artists'][0]['id']
#
#         self.album_group = self.sp_record['album_group']
#         self.album_type = self.sp_record['album_type']
#
#         self.release_date = release_date
#         self.release_date_precision = release_date_precision
#
#
# class Track_(Media_):
#     def __post_init__(self):
#         super().__post_init__()
#         self.artist = self.sp_record['artists'][0]['name']
#         self.artist_id = self.sp_record['artists'][0]['id']
#
#
# class Artist_(Media_):
#     def __post_init__(self):
#         super().__post_init__()
#
