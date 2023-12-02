from datetime import datetime
from pathlib import Path
from typing import List, Literal

import spotipy as sp

from ..media_model import ReleaseDict, TrackDict

scope = ('user-library-read user-follow-read playlist-modify-private '
         'user-read-playback-state user-read-currently-playing playlist-modify-public')


def all_tracks_from_artists(spotify: sp.Spotify, artist_ids: List[str]) -> List[TrackDict]:
    releases = releases_from_artist_ids(spotify, artist_ids)
    release_ids = [_.id for _ in releases]
    track_dicts = tracks_from_release_ids(spotify, release_ids)
    return track_dicts


def releases_from_artist_ids(spotify: sp.Spotify, artist_ids: List[str]) -> List[ReleaseDict]:
    """Fetches releases for a list of artist IDs.
        Results from artist_albums endpoint lack track data"""
    rd_list = []
    for artist_id in artist_ids:
        results = spotify.artist_albums(artist_id, limit=1)
        albums = _expand_sp_results(results, spotify)
        release_dictys = [ReleaseDict(release) for release in albums]
        rd_list.extend(release_dictys)
    return rd_list


def tracks_from_release_ids(spotify: sp.Spotify, release_ids: List[TrackDict]):
    return [TrackDict(track) for release_id in release_ids
            for track in spotify.album_tracks(release_id)['items']]


def _imprecise_date(input_date_string: str,
                    precision: Literal['day', 'month', 'year']) -> datetime.date:
    if precision == 'year':
        input_date_string = input_date_string[:4]
        stripped_date = datetime.strptime(input_date_string, "%Y").date()
    elif precision == 'month':
        input_date_string = input_date_string[:7]
        stripped_date = datetime.strptime(input_date_string, "%Y-%m").date()
    else:
        stripped_date = datetime.strptime(input_date_string, "%Y-%m-%d").date()

    return stripped_date


def _expand_sp_results(results, spotify: sp.Spotify):
    all_res = []
    while True:
        all_res.extend(results['items'])
        if not results['next']:
            break
        results = spotify.next(results)
    return all_res


def build_search_query(form):
    search_dict = {cond: form.data[cond] for cond in ['artist', 'album', 'year'] if form.data[cond]}
    category = ','.join(form.category.data).replace(" ",
                                                    "") if "any" not in form.category.data else "artist,album,track,playlist"
    search_string = form.search_term.data if 'search_term' in form.data else ''
    for constraint, value in search_dict.items():
        search_string += f" {constraint}:{value}"
    return search_string, category


def perform_spotify_search(spotify, search_string, category):
    response = spotify.search(q=search_string, type=category, limit=50)
    results_dict = {media_type: response[media_type]['items'] for media_type in response if
                    response[media_type]['items']}

    for media_type, items in results_dict.items():
        while response[media_type]['next'] and response[media_type]['offset'] < 950:
            next_page = spotify.next(response[media_type])
            items.extend(next_page[media_type]['items'])

    return results_dict


def sort_results(results_dict):
    sort_funcs = {
        'artists': lambda x: (x['name'].lower(), -x['followers']['total']),
        'albums': lambda x: (x['artists'][0]['name'].lower(), x['name'].lower()),
        'tracks': lambda x: (
            x['artists'][0]['name'].lower(), x['album']['name'].lower(), x['name'].lower()),
        'playlists': lambda x: x['name'].lower()
    }

    return {media_type: sorted(items, key=sort_funcs[media_type]) for media_type, items in
            results_dict.items()}


def get_spooty(session_cache: Path):
    cache_handler = sp.cache_handler.CacheFileHandler(session_cache)
    auth_manager = sp.oauth2.SpotifyOAuth(scope=scope, cache_handler=cache_handler,
                                          show_dialog=True)
    return sp.Spotify(auth_manager=auth_manager)
