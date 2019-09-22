# coding: utf-8

from ething.plugin import Plugin
from ething.account import Account
from ething.reg import *
from ething.scheduler import set_interval
import logging
import spotipy
import spotipy.oauth2


LOGGER = logging.getLogger(__name__)


class SpotifyOAuth_(spotipy.oauth2.SpotifyOAuth):
    def get_authorize_url(self, state=None):
        return super(SpotifyOAuth_, self).get_authorize_url(state) + '&show_dialog=true'

    def _warn(self, msg):
        LOGGER.warning(msg)


class Spotify(Plugin):

    JS_INDEX = './js/index.js'

    def load(self):
        self._current_account = None

    def setup(self):
        # install specific http routes
        self._webserver_install()

    def _webserver_install(self):

        # install specific http routes

        app = self.core.plugins['webserver'].app
        auth = app.auth

        from flask import request, redirect, url_for

        @app.route('/api/spotify/login')
        @auth.required()
        def spotify_login():
            account = self.core.get(request.args.get('resource'))
            redirect_uri = re.sub('/api/spotify/login.*$', '/api/spotify/auth', request.url)
            authorize_url = account.oauth(redirect_uri).get_authorize_url()
            LOGGER.debug('login authorize_url=%s', authorize_url)
            self._current_account = account
            return redirect(authorize_url, code=302)

        @app.route('/api/spotify/auth')
        @auth.required()
        def spotify_authorize():
            redirect_uri = re.sub('/api/spotify/auth.*$', '/api/spotify/auth', request.url)
            token_info = self._current_account.oauth(redirect_uri).get_access_token(request.args.get("code"))
            LOGGER.debug('auth token_info=%s', token_info)
            if token_info:
                self._current_account.token = dict(token_info)
            self._current_account = None
            return redirect(url_for('root_client'), code=302)


@attr('title', mode=READ_ONLY, default=None)
@attr('artist', mode=READ_ONLY, default=None)
@attr('album', mode=READ_ONLY, default=None)
@attr('user', mode=READ_ONLY, default=None)
@attr('shuffle', mode=READ_ONLY, default=None)
@attr('volume', mode=READ_ONLY, default=None)
@attr('current_device', mode=READ_ONLY, default=None)
@attr('_token', mode=PRIVATE, default=None)
@attr('client_secret', label="client secret", type=String(allow_empty=False))
@attr('client_id', label="client id", type=String(allow_empty=False))
@meta(icon="mdi-spotify", loginUrl='/spotify/login')
class SpotifyAccount(Account):

    def __init__(self, *args, **kwargs):
        super(SpotifyAccount, self).__init__(*args, **kwargs)
        self.logged = bool(self.token)
        self._player = None

    def oauth(self, redirect_uri = None):
        return SpotifyOAuth_(
            self.client_id,
            self.client_secret,
            redirect_uri,
            scope='user-read-email playlist-read-private user-read-playback-state user-read-currently-playing user-modify-playback-state',
        )

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        with self:
            self._token = value
            self._player = None # reset the player
            self.logged = bool(value)

    @set_interval(60, name="spotify.refresh_token")
    def refresh_token(self, force=False):
        token = self.token
        if not token:
            return
        # refresh only if necessary
        oauth = self.oauth()
        if force or spotipy.oauth2.is_token_expired(token):
            self.token = oauth.refresh_access_token(token['refresh_token'])

    @property
    def player(self):
        if self._player is None:
            kwargs = {}
            token = self.token
            if token:
                kwargs['auth'] = token.get("access_token")
            self._player = spotipy.Spotify(**kwargs)
        return self._player

    @method.return_type('object')
    def current_user(self):
        return self.player.current_user()

    @method.return_type('object')
    def current_playback(self):
        return self.player.current_playback()

    @method.return_type('object')
    def currently_playing(self):
        return self.player.currently_playing()

    @method.return_type('object')
    def current_user_playlists(self, limit=50, offset=0):
        return self.player.current_user_playlists(limit, offset)

    @method.return_type('object')
    def current_user_saved_albums(self, limit=20, offset=0):
        return self.player.current_user_saved_albums(limit, offset)

    @method.return_type('object')
    def current_user_top_artists(self, limit=20, offset=0):
        return self.player.current_user_top_artists(limit, offset)

    @method.return_type('object')
    def devices(self):
        return self.player.devices()

    @method.attr('device_id', type=Nullable(String(allow_empty=False)), default=None)
    def next_track(self, device_id=None):
        return self.player.next_track(device_id)

    @method.attr('device_id', type=Nullable(String(allow_empty=False)), default=None)
    def pause_playback(self, device_id=None):
        return self.player.pause_playback(device_id)

    @method.attr('uris', type=Nullable(Array(String(allow_empty=False))), default=None)
    @method.attr('context_uri', type=Nullable(String(allow_empty=False)), default=None)
    @method.attr('device_id', type=Nullable(String(allow_empty=False)), default=None)
    def start_playback(self, device_id=None, context_uri=None, uris=None):
        return self.player.start_playback(device_id, context_uri, uris)

    @method.attr('device_id', type=Nullable(String(allow_empty=False)), default=None)
    def previous_track(self, device_id=None):
        return self.player.previous_track(device_id)

    @method.attr('device_id', type=Nullable(String(allow_empty=False)), default=None)
    @method.attr('state', type=Enum(('track', 'context', 'off')))
    def repeat(self, state, device_id=None):
        return self.player.repeat(state, device_id)

    @method.attr('device_id', type=Nullable(String(allow_empty=False)), default=None)
    @method.attr('state', type=Boolean())
    def shuffle(self, state, device_id=None):
        return self.player.shuffle(state, device_id)

    @method.attr('device_id', type=String(allow_empty=False))
    def transfer_playback(self, device_id, force_play=True):
        return self.player.transfer_playback(device_id, force_play)

    @method.attr('device_id', type=Nullable(String(allow_empty=False)))
    @method.attr('volume_percent', type=Number(min=0, max=100))
    def volume(self, volume_percent, device_id=None):
        return self.player.volume(volume_percent, device_id)

