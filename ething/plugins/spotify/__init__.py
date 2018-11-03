# coding: utf-8

from ething.core.plugin import Plugin
from ething.core.Device import Device
from ething.core.reg import *
from ething.core.ShortId import ShortId
from flask import redirect, request, url_for
import re
import base64
import requests
import time
import json

# Workaround to support both python 2 & 3
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


# todo: auto refresh

OAUTH_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'
WEB_API_URL = 'https://api.spotify.com/v1/'

SCOPE = 'playlist-read-private user-read-playback-state user-read-currently-playing user-modify-playback-state'

REFRESH_TOKEN_SURVEY_INTERVAL = 300

def make_authorization_headers(client_id, client_secret):
    auth_header = "%s:%s" % (client_id, client_secret)
    auth_header = base64.b64encode(auth_header.encode('ascii'))
    return {
        'Authorization': 'Basic %s' % auth_header.decode('ascii')
    }


class spotify(Plugin):

    def load(self):
        super(spotify, self).load()

        self._survey_task = self.core.scheduler.setInterval(REFRESH_TOKEN_SURVEY_INTERVAL, self._refresh_token_survey, name='spotify.refresh_token', thread=True)

        # install specific http routes
        webserver_plugin = self.core.get_plugin('WebServer')
        if webserver_plugin:
            webserver_plugin.register_installer(self._webserver_install)

    def _webserver_install(self, app, auth, **kwargs):

        _states = dict()

        @app.route('/api/resources/<id>/spotify/login')
        @auth.required()
        def spotify_login(id):

            r = app.getResource(id, ['SpotifyAccount'])

            redirect_uri = re.sub('/api/resources/.*$', '/api/spotify/callback', request.url)

            state = ShortId.generate()

            _states[state] = {
                'oauth_redirect_uri': redirect_uri,
                'resource': r.id,
                'scope': SCOPE,
                'redirect_uri': request.args.get('redirect_uri')
            }

            payload = {
                'client_id': r.client_id,
                'response_type': 'code',
                'redirect_uri': redirect_uri,
                'state': state,
                'scope': SCOPE
            }

            urlparams = urlencode(payload)

            url = "%s?%s" % (OAUTH_AUTHORIZE_URL, urlparams)

            return redirect(url, code=302)

        @app.route('/api/spotify/callback')
        @auth.required()
        def spotify_callback():

            error = request.args.get('error')

            if error:
                raise Exception(error)

            code = request.args.get('code')
            state = request.args.get('state')

            if state not in _states:
                raise Exception('invalid state')

            redirect_uri = _states[state].get('redirect_uri')
            r = app.getResource(_states[state].get('resource'), ['SpotifyAccount'])

            payload = {
                'redirect_uri': _states[state].get('oauth_redirect_uri'),
                'code': code,
                'grant_type': 'authorization_code'
            }

            headers = make_authorization_headers(r.client_id, r.client_secret)

            response = requests.post(OAUTH_TOKEN_URL, data=payload, headers=headers, verify=True)
            if response.status_code != 200:
                raise Exception(response.reason)
            token_info = response.json()

            access_token = token_info['access_token']
            refresh_token = token_info['refresh_token']
            scope = token_info['scope']
            expires_in = token_info['expires_in']
            expires_at = int(time.time()) + expires_in

            with r:
                r.access_token = access_token
                r.refresh_token = refresh_token
                r.access_token_expires_at = expires_at

            if not redirect_uri:
                redirect_uri = url_for('static_client', path='index.html')

            return redirect(redirect_uri, code=302)

    def unload(self):
        if hasattr(self, '_survey_task'):
            self.core.scheduler.unbind(self._survey_task)

    def _refresh_token_survey(self):
        self.log.debug('verify refresh tokens ...')
        accounts = self.core.find(lambda r: r.isTypeof('resources/SpotifyAccount'))
        for account in accounts:
            if account._is_token_expired(offset=2 * REFRESH_TOKEN_SURVEY_INTERVAL):
                account._refresh_access_token()


RETRIES = 3
REQUESTS_TIMEOUT = None


class SpotifyException(Exception):
    def __init__(self, http_status, code, msg, headers=None):
        self.http_status = http_status
        self.code = code
        self.msg = msg
        # `headers` is used to support `Retry-After` in the event of a
        # 429 status code.
        if headers is None:
            headers = {}
        self.headers = headers

    def __str__(self):
        return 'http status: {0}, code:{1} - {2}'.format(
            self.http_status, self.code, self.msg)


@attr('access_token_expires_at', default=None, mode = PRIVATE)
@attr('access_token', default=None, mode = READ_ONLY)
@attr('refresh_token', default=None, mode = PRIVATE)
@attr('client_secret', type=String(allow_empty=False), description="Your secret.")
@attr('client_id', type=String(allow_empty=False), description="Your client id.")
class SpotifyAccount (Device):

    def _is_token_expired(self, offset = 0):
        now = int(time.time())
        expires_at = self.access_token_expires_at
        return expires_at and expires_at - now < 60 + offset

    def _refresh_access_token(self):
        refresh_token = self.refresh_token

        if not refresh_token:
            self.log.error("no refresh_token")
            return

        payload = {
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

        headers = make_authorization_headers(self.client_id, self.client_secret)

        response = requests.post(OAUTH_TOKEN_URL, data=payload, headers=headers)
        if response.status_code != 200:
            self.log.warning("couldn't refresh token: code:%d reason:%s" % (response.status_code, response.reason))
            return

        token_info = response.json()

        self.log.debug("token refreshed")

        access_token = token_info['access_token']
        expires_in = token_info['expires_in']
        expires_at = int(time.time()) + expires_in

        with self:
            self.access_token = access_token
            self.access_token_expires_at = expires_at



    # cf. https://github.com/plamere/spotipy/blob/master/spotipy/client.py

    def _internal_call(self, method, url, payload, params):

        access_token = self.access_token

        if not access_token:
            raise Exception('Not connected')

        args = dict(params=params)
        args["timeout"] = REQUESTS_TIMEOUT

        if not url.startswith('http'):
            url = WEB_API_URL + url

        headers = {
            'Authorization': 'Bearer {0}'.format(access_token)
        }
        headers['Content-Type'] = 'application/json'

        if payload:
            args["data"] = json.dumps(payload)

        self.log.debug('request: %s %s' % (method, url))

        r = requests.request(method, url, headers=headers, **args)

        self.log.debug('request status: %s' % (r.status_code))

        try:
            r.raise_for_status()
        except:
            if r.text and len(r.text) > 0 and r.text != 'null':
                raise SpotifyException(r.status_code,
                                       -1, '%s:\n %s' % (r.url, r.json()['error']['message']),
                                       headers=r.headers)
            else:
                raise SpotifyException(r.status_code,
                                       -1, '%s:\n %s' % (r.url, 'error'), headers=r.headers)
        finally:
            r.close()

        if r.text and len(r.text) > 0 and r.text != 'null':
            results = r.json()
            return results
        else:
            return None

    def _get_request(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)

        retries = RETRIES
        delay = 1
        while retries > 0:
            try:
                return self._internal_call('GET', url, payload, kwargs)
            except SpotifyException as e:
                retries -= 1
                status = e.http_status
                # 429 means we hit a rate limit, backoff
                if status == 429 or (status >= 500 and status < 600):
                    if retries < 0:
                        raise
                    else:
                        sleep_seconds = int(e.headers.get('Retry-After', delay))
                        time.sleep(sleep_seconds + 1)
                        delay += 1
                else:
                    raise

    def _post_request(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._internal_call('POST', url, payload, kwargs)

    def _delete_request(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._internal_call('DELETE', url, payload, kwargs)

    def _put_request(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._internal_call('PUT', url, payload, kwargs)

    @method
    def listDevices(self):
        ''' Get a list of user's available devices.
        '''
        return self._get_request("me/player/devices")

    def current_playback(self, market=None):
        ''' Get information about user's current playback.
            Parameters:
                - market - an ISO 3166-1 alpha-2 country code.
        '''
        return self._get_request("me/player", market=market)

    @method
    def listPlaylists(self, limit=50, offset=0):
        """ Get current user playlists without required getting his profile
            Parameters:
                - limit  - the number of items to return
                - offset - the index of the first item to return
        """
        return self._get_request("me/playlists", limit=limit, offset=offset)

