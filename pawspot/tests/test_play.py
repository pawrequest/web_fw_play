from datetime import datetime
from itertools import product
from pprint import pprint

import pytest
import spotipy as sp
from dotenv import load_dotenv
from flask import redirect

from paul_sees_spotify.spoti_funcs.spot_funcs import date_stripper_og as date_stripper
# from paul_sees_spotify.application.new_func import date_stripper2 as date_stripper
# from paul_sees_spotify.application.spotify_functions import date_stripper

load_dotenv()
scope = "user-library-read, user-read-playback-state, user-follow-read", "playlist-modify-public"
artist_id = '3xjNFu3aAWJie7LQzDoYNa'


# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
# sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

def test_smth():
    # cache_handler = sp.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = sp.oauth2.SpotifyOAuth()
    tok = auth_manager.get_access_token()
    if not auth_manager.validate_token(tok):
        return redirect('/')
    spotify = sp.Spotify(auth_manager=auth_manager)
    results = spotify.artist_albums(artist_id)
    pprint(results)


# Separate lists of input strings and precisions
input_dates = ["2023-03-15", "2023-03", "2023", "invalid-date", "2023-03-15-extra"]
precisions = ["day", "month", "year", "invalid"]


# Expected behavior function
def expected_behavior(input_date, precision) ->datetime:
    try:
        if precision == 'day':
            return datetime.strptime(input_date, "%Y-%m-%d")
        elif precision == 'month':
            return datetime.strptime(input_date[:7], "%Y-%m")
        elif precision == 'year':
            return datetime.strptime(input_date[:4], "%Y")
    except ValueError:
        return input_date  # Return the input date string for invalid cases


# Create test cases using product of input_dates and precisions
test_cases = list(product(input_dates, precisions))


# Parameterized test function
@pytest.mark.parametrize("input_date,precision", test_cases)
def test_date_stripper(input_date, precision):
    expected = expected_behavior(input_date, precision)
    res = date_stripper(input_date, precision)
    assert res == expected
