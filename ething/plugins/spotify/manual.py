# coding: utf-8

from ething.plugin import Plugin
from ething.reg import *
from ething import Device
from ething.utils.date import TzDate, utcnow
from ething.scheduler import set_interval

from authlib.client import OAuth2Session

import logging
import pickle


LOGGER = logging.getLogger(__name__)


ACCESS_TOKEN_URI = 'https://accounts.spotify.com/api/token'
AUTHORIZATION_URL = 'https://accounts.spotify.com/authorize?show_dialog=true'

API_BASE_URL = 'https://api.spotify.com/v1/'

AUTHORIZATION_SCOPE = 'user-read-email playlist-read-private user-read-playback-state user-read-currently-playing user-modify-playback-state'

AUTH_STATE_KEY = 'auth_state'
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

        raw_users_data = self.core.db.store.get(USERS_KEY, None)
        if raw_users_data is not None:
            self.users = pickle.loads(raw_users_data)

    def setup(self):
        # install specific http routes
        self._webserver_install()

    @set_interval(30, name="spotify.test")
    def test(self):
        for user in self.users:
            LOGGER.debug('spotify/test')
            oauth2_session = OAuth2Session(token=user.tokens)
            resp = oauth2_session.request('GET', API_BASE_URL + 'me/player/devices')
            LOGGER.debug('spotify/test resp=%s', resp)
            data = resp.json()
            LOGGER.debug('spotify/test data=%s', data)

    def _webserver_install(self):

        # install specific http routes
        webserver_plugin = self.core.plugins['webserver']
        if not webserver_plugin:
            return

        app = webserver_plugin.app
        auth = app.auth

        from flask import request, redirect, url_for, Response

        @app.route('/api/spotify/login')
        @auth.required()
        def spotify_login():
            if not self.client_id or not self.client_secret:
                raise Exception('no client_id or client_secret set')

            redirect_uri = re.sub('/api/spotify/login.*$', '/api/spotify/auth', request.url)

            LOGGER.debug('spotify/login client_id=%s client_secret=%s scope=%s redirect_uri=%s', self.client_id, self.client_secret, AUTHORIZATION_SCOPE, redirect_uri)

            oauth2_session = OAuth2Session(self.client_id, self.client_secret, scope=AUTHORIZATION_SCOPE, redirect_uri=redirect_uri)

            uri, state = oauth2_session.create_authorization_url(AUTHORIZATION_URL)

            LOGGER.debug('spotify/login uri=%s, state=%s', uri, state)

            self.session[AUTH_STATE_KEY] = state

            return redirect(uri, code=302)

        @app.route('/api/spotify/auth')
        @auth.required()
        def spotify_authorize():

            if not self.client_id or not self.client_secret:
                raise Exception('no client_id or client_secret set')

            req_state = request.args.get('state', default=None, type=None)

            if req_state != self.session[AUTH_STATE_KEY]:
                raise Exception('Invalid state parameter')

            redirect_uri = re.sub('/api/spotify/auth.*$', '/api/spotify/auth', request.url)

            LOGGER.debug('spotify/auth client_id=%s client_secret=%s scope=%s redirect_uri=%s state=%s', self.client_id,
                         self.client_secret, AUTHORIZATION_SCOPE, redirect_uri, self.session[AUTH_STATE_KEY])

            oauth2_session = OAuth2Session(self.client_id, self.client_secret,
                                    scope=AUTHORIZATION_SCOPE,
                                    state=self.session[AUTH_STATE_KEY],
                                    redirect_uri=redirect_uri)

            oauth2_tokens = oauth2_session.fetch_access_token(
                ACCESS_TOKEN_URI,
                authorization_response=request.url)

            LOGGER.debug('spotify/auth oauth2_tokens=%s', oauth2_tokens)

            # fetch user information
            resp = oauth2_session.request('GET', API_BASE_URL + 'me')
            LOGGER.debug('spotify/auth resp=%s', resp)

            user_info = resp.json()
            LOGGER.debug('spotify/auth user_info=%s', user_info)
            # do something with the token and profile
            self._add_user(user_info, oauth2_tokens)

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

