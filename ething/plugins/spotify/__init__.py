# coding: utf-8

from ething.plugin import Plugin
from ething.account import Account
from ething.reg import *
from ething.scheduler import set_interval
from ething.env import USER_DIR
import logging
import pickle
from spotipy.oauth2 import SpotifyOAuth
import os


LOGGER = logging.getLogger(__name__)


class SpotifyOAuth_(SpotifyOAuth):

    def get_authorize_url(self, redirect_uri=None):
        if redirect_uri:
            self.redirect_uri = redirect_uri
        return super(SpotifyOAuth_, self).get_authorize_url() + '&show_dialog=true'

    def get_access_token(self, code, redirect_uri=None):
        if redirect_uri:
            self.redirect_uri = redirect_uri
        return super(SpotifyOAuth_, self).get_access_token(code)


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
            authorize_url = account.oauth.get_authorize_url(redirect_uri)
            LOGGER.debug('login authorize_url=%s', authorize_url)
            self._current_account = account
            return redirect(authorize_url, code=302)

        @app.route('/api/spotify/auth')
        @auth.required()
        def spotify_authorize():
            redirect_uri = re.sub('/api/spotify/auth.*$', '/api/spotify/auth', request.url)
            token_info = self._current_account.oauth.get_access_token(request.args.get("code"), redirect_uri) # auto saved in cache
            LOGGER.debug('auth token_info=%s', token_info)
            self._current_account.logged = True
            self._current_account = None
            return redirect(url_for('root_client'), code=302)


@attr('client_secret', label="client secret", type=String(allow_empty=False))
@attr('client_id', label="client id", type=String(allow_empty=False))
@meta(icon="mdi-spotify", loginUrl='/spotify/login')
class SpotifyAccount(Account):

    def __init__(self, *args, **kwargs):
        super(SpotifyAccount, self).__init__(*args, **kwargs)

        self.oauth = SpotifyOAuth_(
            self.client_id,
            self.client_secret,
            None,
            scope='user-read-email playlist-read-private user-read-playback-state user-read-currently-playing user-modify-playback-state',
            cache_path=os.path.abspath(os.path.join(USER_DIR, 'spotify_%s.json' % self.id)),
        )

        token_info = self.oauth.get_cached_token()
        self.logged = bool(token_info)


