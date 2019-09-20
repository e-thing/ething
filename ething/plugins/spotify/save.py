# coding: utf-8

from ething.plugin import Plugin
from ething.reg import *
from ething.scheduler import set_interval
import logging
import pickle


LOGGER = logging.getLogger(__name__)


USERS_KEY = 'spotify_users'


class SpotifyUserNotLoggedException(Exception):
    pass


@attr('client_secret', label="client secret", type=String(), default='')
@attr('client_id', label="client id", type=String(), default='')
class Spotify(Plugin):

    JS_INDEX = './js/index.js'

    def load(self):
        self.users = list()
        self.session = dict()
        self._remote_app = None

        raw_users_data = self.core.db.store.get(USERS_KEY, None)
        if raw_users_data is not None:
            self.users = pickle.loads(raw_users_data)

    def setup(self):
        # install specific http routes
        self._webserver_install()

    def on_config_change(self, dirty_attributes):
        # clear remote app
        self._remote_app = None
        oauth = self.core.plugins['webserver'].app.oauth
        oauth._clients.pop('spotify', None)

    def remote_app(self):
        if not self._remote_app:
            if not self.client_id or not self.client_secret:
                raise Exception('no client_id or client_secret set')
            oauth = self.core.plugins['webserver'].app.oauth
            oauth.register(
                name='spotify',
                client_id=self.client_id,
                client_secret=self.client_secret,
                access_token_url='https://accounts.spotify.com/api/token',
                authorize_url='https://accounts.spotify.com/authorize?show_dialog=true',
                api_base_url='https://api.spotify.com/v1/',
                client_kwargs={'scope': 'user-read-email playlist-read-private user-read-playback-state user-read-currently-playing user-modify-playback-state'},
            )
            self._remote_app = oauth.spotify
        return self._remote_app

    @set_interval(30, name="spotify.test")
    def test(self):
        for user in self.users:
            LOGGER.debug('spotify/test')
            resp = self.request('GET', 'me/player/devices', user)
            LOGGER.debug('spotify/test resp=%s', resp)
            data = resp.json()
            LOGGER.debug('spotify/test data=%s', data)

    def request(self, method, url, user, **kwargs):
        if isinstance(user, string_types):
            user = self.find_user(user)
        return self.remote_app().request(method, url, token=user.tokens, **kwargs)

    def _webserver_install(self):

        # install specific http routes

        app = self.core.plugins['webserver'].app
        auth = app.auth

        from flask import request, redirect, url_for

        @app.route('/api/spotify/login')
        @auth.required()
        def spotify_login():
            redirect_uri = re.sub('/api/spotify/login.*$', '/api/spotify/auth', request.url)
            LOGGER.debug('spotify/login redirect_uri=%s', redirect_uri)
            return self.remote_app().authorize_redirect(redirect_uri)

        @app.route('/api/spotify/auth')
        @auth.required()
        def spotify_authorize():

            tokens = self.remote_app().authorize_access_token()
            resp = self.remote_app().get('me')
            profile = resp.json()
            LOGGER.debug('spotify/auth profile=%s', profile)
            # do something with the token and profile
            self._add_user(profile, tokens)

            return redirect(url_for('root_client'), code=302)

        @app.route('/api/spotify/logout/<user_id>')
        @auth.required()
        def spotify_logout(user_id):
            LOGGER.debug('spotify/logout')
            self._remove_user(user_id)
            return '', 204

        @app.route('/api/spotify/users')
        @auth.required()
        def spotify_list_users():
            return app.jsonify(self.users)

    def _add_user(self, user_info, oauth2_tokens):

        user = SpotifyUser(user_info, oauth2_tokens)

        if user in self.users:
            self.users.remove(user)

        self.users.append(user)

        self.save()

    def _remove_user(self, user):
        if user in self.users:
            self.users.remove(user)
        self.save()

    def save(self):
        self.core.db.store[USERS_KEY] = pickle.dumps(self.users)

    def find_user(self, user_id):
        if user_id in self.users:
            i = self.users.index(user_id)
            return self.users[i]
        else:
            raise SpotifyUserNotLoggedException()


class SpotifyUser(object):

    def __init__(self, user_info, oauth2_tokens):
        self._user_info = user_info
        self._tokens = oauth2_tokens

    @property
    def id(self):
        return self._user_info.get('id')

    @property
    def tokens(self):
        return self._tokens

    def __eq__(self, other):
        if isinstance(other, SpotifyUser):
            return self.id == other.id
        elif isinstance(other, string_types):
            return self.id == other
        else:
            return False

    def __json__(self):
        return self._user_info


class SpotifyUserType(String):
    def __init__(self, **attr):
        super(SpotifyUserType, self).__init__(allow_empty=False, **attr)

    def to_shema(self, context = None):
        s = super(SpotifyUserType, self).to_shema(context)
        s['$component'] = 'SpotifyUserForm'
        return s
