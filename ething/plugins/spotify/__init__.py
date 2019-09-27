# coding: utf-8

from ething.plugin import Plugin
from ething.Device import Device
from ething.reg import *
from ething.scheduler import set_interval, delay
import logging
import spotipy
import spotipy.oauth2


LOGGER = logging.getLogger(__name__)


UPDATE_INTERVAL = 30
UPDATE_DELAY = 0.5


class SpotifyOAuth_(spotipy.oauth2.SpotifyOAuth):
    def get_authorize_url(self, state=None):
        return super(SpotifyOAuth_, self).get_authorize_url(state) + '&show_dialog=true'

    def _warn(self, msg):
        LOGGER.warning(msg)


class Spotify_(spotipy.Spotify):

    def _append_device_id(self, path, device_id):
        # replace the buggy version
        if device_id:
            path += '&' if ('?' in path) else '?'
            path += "device_id=%s" % device_id
        return path


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


@attr('image_url', mode=READ_ONLY, default=None)
@attr('uri', mode=READ_ONLY, default=None)
@attr('title', mode=READ_ONLY, default=None)
@attr('artist', mode=READ_ONLY, default=None)
@attr('album', mode=READ_ONLY, default=None)
@attr('user', mode=READ_ONLY, default=None)
@attr('repeat', mode=READ_ONLY, default='off')
@attr('shuffle', mode=READ_ONLY, default=False)
@attr('current_device', mode=READ_ONLY, default=None)
@attr('state', type=Enum(('playing', 'paused', 'idle')), default='idle', mode=READ_ONLY, description="current state")
@attr('_token', mode=PRIVATE, default=None)
@attr('client_secret', label="client secret", type=String(allow_empty=False))
@attr('client_id', label="client id", type=String(allow_empty=False))
@meta(icon="mdi-spotify", description="""
1. Login to [Spotify Developer](https://developer.spotify.com/dashboard)
2. Select **Create An App**. Enter any name and description. Once your application is created, view it and copy your **Client ID** and **Client Secret**.
3. Add a Redirect URI in one of the following forms:
```
# replace <ething-server-ip> by the ip address of your ething server.
http://<ething-server-ip>:8000/api/spotify/auth
```
""")
class SpotifyAccount(Device):

    def __init__(self, *args, **kwargs):
        super(SpotifyAccount, self).__init__(*args, **kwargs)
        self.connected = bool(self.token)
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
            self.connected = bool(value)

    def refresh_token(self, force=False):
        token = self.token
        if not token:
            return
        # refresh only if necessary
        oauth = self.oauth()
        if force or spotipy.oauth2.is_token_expired(token):
            self.logger.debug('refresh_access_token')
            self.token = oauth.refresh_access_token(token['refresh_token'])

    @set_interval(UPDATE_INTERVAL, name="spotify.poll")
    def update(self):
        self.refresh_token()

        if not self.user:
            user_info = self.player.current_user()
            if user_info:
                self.user = {
                    'name': user_info.get('display_name'),
                    'email': user_info.get('email'),
                    'uri': user_info.get('uri'),
                }

        self.update_state()

    def update_state(self):

        self.logger.debug('update_state')

        playback = self.current_playback()

        with self:

            self.refresh_connect_state(True)

            if playback:
                # something is playing

                device = playback.get('device')

                if device:
                    self.state = 'playing' if playback.get("is_playing") else 'paused'
                    self.current_device = {
                        'name': device.get('name', 'unknown'),
                        'id': device.get('id'),
                        'volume': device.get('volume_percent', 100)
                    }
                else:
                    self.state = 'idle'

                self.shuffle = playback.get('shuffle_state', False)
                self.repeat = playback.get('repeat_state', 'off')

                item = playback.get("item")

                if item:
                    self.album = item.get("album").get("name")
                    self.title = item.get("name")
                    self.artist = ", ".join(
                        [artist.get("name") for artist in item.get("artists")]
                    )
                    self.uri = item.get("uri")
                    images = item.get("album").get("images")
                    self.image_url = images[0].get("url") if images else None
                else:
                    self.album = None
                    self.artist = None
                    self.title = None
                    self.uri = None
                    self.image_url = None

            else:
                self.state = 'idle'
                self.album = None
                self.artist = None
                self.title = None
                self.uri = None
                self.image_url = None


    @property
    def player(self):
        if self._player is None:
            kwargs = {}
            token = self.token
            if token:
                kwargs['auth'] = token.get("access_token")
            self._player = Spotify_(**kwargs)
        return self._player

    @method.return_type('object')
    def current_user(self):
        return self.player.current_user()

    @method.return_type('object')
    def current_playback(self):
        """
        Get information about the user’s current playback state, including track, track progress, and active device.
        """
        return self.player.current_playback()

    #@method.return_type('object')
    #def currently_playing(self): # better use current_playback()
    #    return self.player.currently_playing()

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
        """
        Get information about a user’s available devices.
        """
        return self.player.devices()

    @method.arg('device_id', type=Nullable(String(allow_empty=False)), default=None)
    def next_track(self, device_id=None):
        self.player.next_track(device_id)
        delay(UPDATE_DELAY, self.update_state)

    @method.arg('device_id', type=Nullable(String(allow_empty=False)), default=None)
    def pause_playback(self, device_id=None):
        self.player.pause_playback(device_id)
        delay(UPDATE_DELAY, self.update_state)

    @method.arg('offset', type=Nullable(Dict()), default=None)
    @method.arg('uris', type=Nullable(Array(String(allow_empty=False))), default=None)
    @method.arg('context_uri', type=Nullable(String(allow_empty=False)), default=None)
    @method.arg('device_id', type=Nullable(String(allow_empty=False)), default=None)
    def start_playback(self, device_id=None, context_uri=None, uris=None, offset=None):
        if offset is not None:
            offset = dict(offset)
        if device_id is None and self.current_device:
            device_id = self.current_device.get('id')
        self.player.start_playback(device_id, context_uri, uris, offset)
        delay(UPDATE_DELAY, self.update_state)

    @method.arg('device_id', type=Nullable(String(allow_empty=False)), default=None)
    def previous_track(self, device_id=None):
        self.player.previous_track(device_id)
        delay(UPDATE_DELAY, self.update_state)

    @method.arg('device_id', type=Nullable(String(allow_empty=False)), default=None)
    @method.arg('state', type=Enum(('track', 'context', 'off')))
    def set_repeat(self, state, device_id=None):
        self.player.repeat(state, device_id)
        delay(UPDATE_DELAY, self.update_state)

    @method.arg('device_id', type=Nullable(String(allow_empty=False)), default=None)
    @method.arg('state', type=Boolean())
    def set_shuffle(self, state, device_id=None):
        self.player.shuffle(state, device_id)
        delay(UPDATE_DELAY, self.update_state)

    @method.arg('device_id', type=String(allow_empty=False))
    def transfer_playback(self, device_id, force_play=True):
        self.player.transfer_playback(device_id, force_play)
        delay(UPDATE_DELAY, self.update_state)

    @method.arg('device_id', type=Nullable(String(allow_empty=False)))
    @method.arg('volume_percent', type=Number(min=0, max=100))
    def set_volume(self, volume_percent, device_id=None):
        self.player.volume(volume_percent, device_id)
        delay(UPDATE_DELAY, self.update_state)

    @method.arg('playlist_id', type=String(allow_empty=False))
    @method.return_type('object')
    def current_user_playlist(self, playlist_id):
        return self.player.user_playlist('me', playlist_id)
