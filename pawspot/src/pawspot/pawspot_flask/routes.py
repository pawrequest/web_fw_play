import os
import uuid

from flask import redirect, render_template, request, session, url_for

from pawspot.media_model import ArtistDict
from pawspot.pawspot_funcs.playlist_maker import check_playlist_exists, make_playlists
from pawspot.pawspot_funcs.spot_funcs import all_tracks_from_artists, build_search_query, \
    get_spooty, perform_spotify_search, sort_results
from . import app, session_cache_path
from .forms import ArtistSelect, ResultsForm, Spot_SearchForm, TracklistForm

ARTIST_IDS = 'artist_ids'


@app.route('/all_artist_tracks', methods=['GET', 'POST'])
def all_artist_tracks():
    spotify = get_spooty(session_cache_path())
    form = ArtistSelect()

    if request.method == 'POST':
        artist = form.artist.data
        results = spotify.search(q=artist, type='artist')
        artists = results['artists']['items']
        session.update({'artists': [ArtistDict(_) for _ in artists]})
        return redirect(url_for('choose_artists'))

    return render_template('all_artist_tracks.html', form=form)


@app.route('/return_artists', methods=['GET', 'POST'])
def choose_artists():
    form = ResultsForm()
    if request.method == 'POST':
        session['selections'] = request.form.getlist('selections')
        return redirect(url_for('show_tracklist'))

    artists = session.get('artists')
    return render_template('return_artists.html', form=form,
                           artists=artists)


@app.route('/show_tracklist', methods=['GET', 'POST'])
def show_tracklist():
    if request.method == 'POST':
        session['playlist_name'] = request.form.get('playlist_name')
        return redirect(url_for('create_playlist'))

    form = TracklistForm()
    spotify = get_spooty(session_cache_path())
    artist_ids = session.get('selections')
    tracks = all_tracks_from_artists(spotify, artist_ids) if artist_ids else []
    session.update({'tracklist': tracks})
    return render_template('show_tracklist.html', form=form, tracks=tracks)


@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    spotify = get_spooty(session_cache_path())
    playlist_title = session.get('playlist_name')

    if check_playlist_exists(spotify, playlist_title):
        print("PLAYLIST EXISTS")
        return redirect(url_for('show_tracklist'))

    tracks = session.get('tracklist', [])
    playlist_ids = make_playlists(spotify=spotify, track_ids=[track.id for track in tracks],
                                  playlist_name=playlist_title)

    session.update({'playlist_title': playlist_title, 'playlist_ids': playlist_ids})
    return redirect(url_for('made_playlist'))


@app.route('/made_playlist')
def made_playlist():
    playlist_title = session.get('playlist_title')
    return render_template('made_playlist.html', playlist_title=playlist_title)


@app.route('/spotauth')
@app.route('/')
def index():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())
    spotify = get_spooty(session_cache_path())
    auth_manager = spotify.auth_manager

    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(auth_manager.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        return render_template('login.html', auth_url=auth_url)

    return render_template('home.html')


@app.route('/sign_out')
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@app.route('/search', methods=['GET', 'POST'])
def search():
    spotify = get_spooty(session_cache_path())
    form = Spot_SearchForm()

    if request.method == 'POST':
        new_search_dict = {}
        for search_condition in ['artist', 'album', 'year']:
            if form.data[search_condition]:
                new_search_dict.update({search_condition: form.data[search_condition]})
        category = form.category.data
        if "any" in category or not category:
            category = "artist,album,track,playlist"  ### ,show,episode ### implement in html....
        else:
            category = ','.join(category)
            category.replace(" ", "")
        if 'search_term' in form.data:
            search_string = form.search_term.data
        else:
            search_string = ''
        if new_search_dict:
            for constraint in new_search_dict:
                search_string = search_string + " " + constraint + ":" + new_search_dict[constraint]
        response = spotify.search(q=search_string, type=category, limit=50)

        # results_list = []
        results_dict = {}
        for media_type in response:
            if response[media_type]['items']:
                results = response[media_type]
                # print (len(results['items']),"RESULTS IN FORMAT",format)
                things = results['items']
                while results['next'] and results['offset'] < 950:
                    # print (len(results['items']),"MORE RESULTS IN FORMAT",format)
                    results = spotify.next(results)
                    results = results[media_type]
                    things.extend(results['items'])
                results_dict.update({media_type: things})
                # results_list.extend(things)

        meta_results_dict = {}
        if 'artists' in results_dict:
            artist_list = results_dict['artists']
            artist_list.sort(key=lambda x: (x['name'].lower(), -x['followers']['total']))
            meta_results_dict.update({'artists': artist_list})
        if 'albums' in results_dict:
            album_list = sorted(results_dict['albums'],
                                key=lambda x: (x['artists'][0]['name'].lower(),
                                               x['name'].lower()))
            meta_results_dict.update({'albums': album_list})
        if 'tracks' in results_dict:
            track_list = sorted(results_dict['tracks'],
                                key=lambda x: (x['artists'][0]['name'].lower(),
                                               x['album']['name'].lower(), x['name'].lower()))
            meta_results_dict.update(({'tracks': track_list}))
        if 'playlists' in results_dict:
            playlist_list = sorted(results_dict['playlists'], key=lambda x: (x['name'].lower()))
            meta_results_dict.update({'playlists': playlist_list})

        # return meta_results_dict
        return render_template(('/search_results.html'), results_dict=results_dict,
                               meta_results_dict=meta_results_dict)

    print('unvalidated')
    return render_template('search.html', form=form)


@app.route('/search', methods=['GET', 'POST'])
def search2():
    spotify = get_spooty(session_cache_path())
    form = Spot_SearchForm()

    if request.method == 'POST':
        search_string, category = build_search_query(form)
        results_dict = perform_spotify_search(spotify, search_string, category)
        meta_results_dict = sort_results(results_dict)

        return render_template('/search_results.html', results_dict=results_dict,
                               meta_results_dict=meta_results_dict)

    return render_template('search.html', form=form)


@app.route('/current_user')
def current_user():
    spotify = get_spooty(session_cache_path())
    current_user = spotify.me()
    return render_template('json_bootstrap.html', user_dict=current_user)


@app.route("/user_analysis")
def analysis():
    # temp_dict = data.to_dict(orient='records')
    # return render_template('results.html', summary = temp_dict)

    spotify = get_spooty(session_cache_path())
    current_user = spotify.current_user()
    return render_template('json_bootstrap.html', user_dict=current_user)


@app.route('/playlists')
def playlists():
    spotify = get_spooty(session_cache_path())
    return spotify.current_user_playlists()


@app.route('/currently_playing')
def currently_playing():
    spotify = get_spooty(session_cache_path())
    track = spotify.current_user_playing_track()
    if track is not None:
        return track
    return "No track currently playing."


# get kap
@app.route('/get_kap')
def get_kap_list():
    # SPOTIPY_REDIRECT_URI = 'http: //127.0.0.1:8080/get_kap'
    # session.update({'next_url':url_for('get_kap_list')})
    # cache_handler = sp.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    # auth_manager = sp.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    # spotify = sp.Spotify(auth_manager=auth_manager)
    spotify = get_spooty(session_cache_path())

    kap_id = 'axaxx6ndw2opzzwztz5xs5me9'
    kap_list = spotify.user_playlists(kap_id)

    playlists = kap_list['items']
    while kap_list['next']:
        kap_list = spotify.next(kap_list)
        playlists.extend(kap_list['items'])
    playlist_dict_list = []
    for item in playlists:
        # playlist ={'id':item['id'], 'name':item['name']}
        playlist_dict_list.append({'name': item['name'], 'id': item['id']})
    # pprint (playlist_dict_list, width=300)
    print(len(playlists))
    for playlist in playlist_dict_list:
        print(playlist['id'])
    ###### BE CAREFULLLLLL!!!!!!!!     spotify.current_user_follow_playlist(play ### #### #### just in case #### ### list['id'])
    return kap_list


@app.route('/search_play', methods=['GET', 'POST'])
def search_play():
    spotify = get_spooty(session_cache_path())
    form = Spot_SearchForm()

    if request.method == 'POST':
        new_search_dict = {}
        for search_condition in ['artist', 'album', 'track', 'year']:
            if form.data[search_condition]:
                new_search_dict.update({search_condition: form.data[search_condition]})
        category = form.category.data
        if "any" in category or not category:
            category = "artist,album,track,playlist"  ### ,show,episode ### implement in html....
        else:
            category = ','.join(category)
            category.replace(" ", "")
        if 'search_term' in form.data:
            search_string = form.search_term.data
        else:
            search_string = ''
        if new_search_dict:
            for constraint in new_search_dict:
                search_string = search_string + " " + constraint + ":" + new_search_dict[constraint]
        response = spotify.search(q=search_string, type=category, limit=50)

        # results_list = []
        results_dict = {}
        for media_type in response:
            if response[media_type]['items']:
                results = response[media_type]
                # print (len(results['items']),"RESULTS IN FORMAT",format)
                things = results['items']
                while results['next'] and results['offset'] < 950:
                    # print (len(results['items']),"MORE RESULTS IN FORMAT",format)
                    results = spotify.next(results)
                    results = results[media_type]
                    things.extend(results['items'])
                results_dict.update({media_type: things})
                # results_list.extend(things)

        meta_results_dict = {}
        if 'artists' in results_dict:
            artist_list = results_dict['artists']
            artist_list.sort(key=lambda x: (x['name'].lower(), -x['followers']['total']))
            meta_results_dict.update({'artists': artist_list})
        if 'albums' in results_dict:
            album_list = sorted(results_dict['albums'],
                                key=lambda x: (x['artists'][0]['name'].lower(),
                                               x['name'].lower()))
            meta_results_dict.update({'albums': album_list})
        if 'tracks' in results_dict:
            track_list = sorted(results_dict['tracks'],
                                key=lambda x: (x['artists'][0]['name'].lower(),
                                               x['album']['name'].lower(), x['name'].lower()))
            meta_results_dict.update(({'tracks': track_list}))
        if 'playlists' in results_dict:
            playlist_list = sorted(results_dict['playlists'], key=lambda x: (x['name'].lower()))
            meta_results_dict.update({'playlists': playlist_list})

        # return meta_results_dict
        return render_template(('/search_results.html'), results_dict=results_dict,
                               meta_results_dict=meta_results_dict)

    print('unvalidated')
    return render_template('/search_play.html', form=form)


@app.route('/return_elaborate', methods=['GET', 'POST'])
def return_elaborate():
    # random_var = request.get
    elaborate_dict_list = session.get('elaborate_dict_list')
    selections = []
    form = ResultsForm()
    # if form.validate():
    if request.method == 'POST':
        # get checkboxes
        own_albums = request.form.get('own_albums')
        own_featured = request.form.get('own_featured')
        own_comp = request.form.get('own_compilations')
        other_own_albums = request.form.get('other_own_albums')
        other_featured = request.form.get('other_featured')
        other_comp = request.form.get('other_compilations')

        selections.extend(request.form.getlist('selections'))
        session.pop('elaborate_selections', None)
        session.update({'elaborate_selections': selections})
        # return "<h1> WEIRD </h1>"
        return redirect(url_for('show_elaborate'))

    return render_template('return_elaborate.html', form=form,
                           elaborate_dict_list=elaborate_dict_list)


@app.route('/elaborate', methods=['GET', 'POST'])
def elaborate_search():
    spotify = get_spooty(session_cache_path())
    form = ArtistSelect()
    if request.method == 'POST':
        # if form.validate():
        artist = form.artist.data
        results = spotify.search(q=artist, type='artist')

        # make a list of dictionaries of results
        elaborate_dict_list = []
        items = results['artists']['items']
        for item in items:
            artist = item['name']
            artist_id = item['id']
            item_dict = {'artist': artist, 'artist_id': artist_id}
            elaborate_dict_list.append(item_dict)
            session.pop('elaborate_dict_list', None)
        session.update({'elaborate_dict_list': elaborate_dict_list})
        return redirect(url_for('return_elaborate'))
    return render_template('elaborate.html', form=form)


@app.route('/show_elaborate', methods=['GET', 'POST'])
def show_elaborate():
    # prepare spotify

    form = TracklistForm()
    selections = session.get('elaborate_selections')
    own_albums = request.form.get('own_albums')
    own_featured = request.form.get('own_featured')
    own_comp = request.form.get('own_compilations')
    other_own_albums = request.form.get('other_own_albums')
    other_featured = request.form.get('other_featured')
    other_comp = request.form.get('other_compilations')
    own_tracks = [own_albums, own_featured, own_comp]
    other_tracks = [other_own_albums, other_featured, other_comp]
    if not any(own_tracks):
        own_tracks = False
    elif all(own_tracks):
        own_tracks = True
    elif any(own_tracks):
        own_tracks = "some"
    if not any(other_tracks):
        other_tracks = False
    elif all(other_tracks):
        other_tracks = True
    elif any(other_tracks):
        other_tracks = "some"

    if request.method == 'POST':
        print("own :", own_tracks, "other", other_tracks)
        return redirect(url_for('made_elaborate'))
    return render_template('show_elaborate.html', form=form)


@app.route('/made_elaborate')
def made_elaborate():
    # playlist_title = session.get('playlist_title')
    return render_template('made_elaborate.html', playlist_title="FAKE TITLE")
