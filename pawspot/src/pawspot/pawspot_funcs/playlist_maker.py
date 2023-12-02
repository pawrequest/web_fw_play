from typing import List

from spotipy import Spotify
PLAYLIST_LIMIT = 2
PLAYLIST_ADD_BATCH = 100

__STEP = 100
MAX_PLAYLIST_LEN = 10000


def check_playlist_exists(spotify: Spotify, playlist_name):
    """ searches current user's playlists for playlist_name = term returns true if exists"""
    limit = 50
    offset = 0
    current_names = []
    for step in range(0, 1000, 50):
        current_playlists = spotify.current_user_playlists(limit=limit, offset=offset)['items']
        for playlist in current_playlists:
            current_names.append(playlist['name'])
        offset += 50
    return playlist_name in current_names


def site_playlist_maker(track_ids, playlist_name, spotify: Spotify):
    if check_playlist_exists(spotify, playlist_name):
        print("PLAYLIST EXISTS")
        return
    track_limit = MAX_PLAYLIST_LEN if len(track_ids) >= MAX_PLAYLIST_LEN else len(track_ids)
    playlist_ids = make_playlists(spotify=spotify, track_ids=track_ids, playlist_name=playlist_name)
    ...


def add_to_playlist(track_ids: List[str], playlist_id: str, spotify: Spotify) -> None:
    for start in range(0, len(track_ids), __STEP):
        batch = track_ids[start:start + __STEP]
        spotify.playlist_add_items(items=batch, playlist_id=playlist_id)


def _make_playlist(spotify, playlist_name='python_play'):
    """creates a playlist on user account, returns playlist_id"""
    user = spotify.me()['id']
    return spotify.user_playlist_create(user=user, name=playlist_name)['id']


def make_playlists(spotify: Spotify, track_ids: List[str], playlist_name: str) -> List[str]:
    num_playlists = (len(track_ids) // MAX_PLAYLIST_LEN) + 1
    playlist_ids = []

    # todo put back
    # for num in range(num_playlists):
    for num in range(PLAYLIST_LIMIT):
        sub_list_ids = track_ids[num * MAX_PLAYLIST_LEN: (num + 1) * MAX_PLAYLIST_LEN]
        sublist_name = f'{playlist_name} part {num}' if num_playlists > 1 else playlist_name
        playlist_id = _make_playlist(spotify, sublist_name)
        playlist_ids.append(playlist_id)
        add_to_playlist(sub_list_ids, playlist_id, spotify)

    return playlist_ids
