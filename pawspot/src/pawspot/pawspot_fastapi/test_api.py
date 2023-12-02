import json
from pathlib import Path

import pytest
import spotipy as sp
from dotenv import load_dotenv
from httpx import AsyncClient
from sqlmodel import SQLModel, Session, create_engine

from pawspot.pawspot_fastapi.media_model import Artist_
from .spotfast import app
from ..pawspot_funcs.spot_funcs import get_spooty

de = r'C:\Users\RYZEN\prdev\pawspot\.env'
load_dotenv(de)


@pytest.fixture
def memory_db():
    engine = create_engine("sqlite:///:memory:")  # Use an in-memory SQLite database for testing
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
        session.rollback()  # Roll back the transaction after the test is done


@pytest.fixture
def file_db():
    engine = create_engine("sqlite:///test.db")  # Use a SQLite database saved to a file for testing
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
        session.rollback()  # Roll back the transaction after the test is done


@pytest.mark.asyncio
async def test_read_main():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200

def test_file_db(file_db):
    ...

def test_memory_db(memory_db):
    ...

@pytest.fixture
def spooty() -> sp.Spotify:
    session_cache = Path(r'C:\Users\RYZEN\prdev\pawspot\src\pawspot\pawspot_fastapi\test_cache')
    auth_manager = sp.oauth2.SpotifyOAuth(cache_path=str(session_cache))

    if session_cache.exists():
        with open(session_cache, 'r') as f:
            token_info = json.load(f)
        if not auth_manager.validate_token(token_info):
            session_cache.unlink()

    yield get_spooty(session_cache)


@pytest.fixture
def search_result_artist(spooty):
    res = spooty.search(q='artist:binbag wisdom', type='artist', limit=1)
    return res['artists']['items'][0]


def test_artist_fixture(search_result_artist):
    assert search_result_artist['name'] == 'Binbag Wisdom'
    assert search_result_artist['id'] == '6VW2IZQIkdS6GmoXDyPoqm'
    assert search_result_artist['external_urls'][
               'spotify'] == 'https://open.spotify.com/artist/6VW2IZQIkdS6GmoXDyPoqm'


def test_artist_model(search_result_artist, file_db):
    ARTY = Artist_(sp_record=search_result_artist)
    file_db.add(ARTY)
    file_db.commit()
    file_db.refresh(ARTY)
    assert ARTY.id_ is not None

# def test_artist_model(search_result_artist):
#     Artist = Artist_(sp_record=search_result_artist)
#     ...
