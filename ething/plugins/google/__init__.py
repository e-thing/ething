# coding: utf-8

from ething.plugin import Plugin
from ething.account import Account
from ething.Resource import ResourceType
from ething.reg import *
from ething import Device
from ething.utils.date import TzDate, utcnow
from ething.scheduler import set_interval

from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

import logging
import requests


LOGGER = logging.getLogger(__name__)


ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'

AUTHORIZATION_SCOPE = 'openid email profile https://www.googleapis.com/auth/calendar.readonly'

AUTH_STATE_KEY = 'auth_state'
ACCOUNT_KEY = 'current_account'

CALENDAR_POLL_INTERVAL = 60


class Google(Plugin):

    JS_INDEX = './js/index.js'

    def load(self):
        self.session = dict()

    def setup(self):
        # install specific http routes
        self._webserver_install()

    def _webserver_install(self):

        # install specific http routes

        app = self.core.plugins['webserver'].app
        auth = app.auth

        from flask import request, redirect, url_for, Response

        @app.route('/api/google/login')
        @auth.required()
        def google_login():
            account = self.core.get(request.args.get('resource'))
            redirect_uri = re.sub('/api/google/login.*$', '/api/google/auth', request.url)

            account.oauth.redirect_uri = redirect_uri

            uri, state = account.oauth.create_authorization_url(AUTHORIZATION_URL)

            self.session[AUTH_STATE_KEY] = state
            self.session[ACCOUNT_KEY] = account

            return redirect(uri, code=302)

        @app.route('/api/google/auth')
        @auth.required()
        def google_authorize():
            account = self.session[ACCOUNT_KEY]

            req_state = request.args.get('state', default=None, type=None)

            if req_state != self.session[AUTH_STATE_KEY]:
                raise Exception('Invalid state parameter')

            redirect_uri = re.sub('/api/google/auth.*$', '/api/google/auth', request.url)
            account.oauth.redirect_uri = redirect_uri

            account.oauth.state = self.session[AUTH_STATE_KEY]

            oauth2_tokens = account.oauth.fetch_access_token(ACCESS_TOKEN_URI, authorization_response=request.url)

            with account:
                account.token = dict(oauth2_tokens)
                account.logged = True

            return redirect(url_for('root_client'), code=302)

        @app.route('/api/google/news')
        @auth.required()
        def google_list_news():
            # https://news.google.com/news/rss
            hl = request.args.get('hl')
            gl = request.args.get('gl')
            params = {}
            if hl:
                params['hl'] = hl
            if gl:
                params['gl'] = gl
            r = requests.get("https://news.google.com/rss", params=params)
            LOGGER.debug('google/news => %s', r.url)
            return Response(r.text, mimetype='text/xml')


@attr('token', mode=PRIVATE, default=None)
@attr('client_secret', label="client secret", type=String(allow_empty=False))
@attr('client_id', label="client id", type=String(allow_empty=False))
@meta(icon="mdi-google", loginUrl='/google/login')
class GoogleAccount(Account):

    def __init__(self, *args, **kwargs):
        super(GoogleAccount, self).__init__(*args, **kwargs)
        self.oauth = OAuth2Session(self.client_id, self.client_secret, scope=AUTHORIZATION_SCOPE, token=self.token)
        self.logged = bool(self.token)

    def _build_credentials(self):
        token = self.token
        if not token:
            raise Exception('not logged in')

        # token.is_expired()

        credentials = google.oauth2.credentials.Credentials(
            token['access_token'],
            refresh_token=token['refresh_token'],
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_uri=ACCESS_TOKEN_URI)

        # todo check if credentials are expired

        return credentials

    def get_calendar_service(self):
        return googleapiclient.discovery.build('calendar', 'v3', credentials=self._build_credentials())


@meta(icon="mdi-calendar")
@attr('events', mode=PRIVATE, default=[])
@attr('contentModifiedDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY, description="Last time the content of this calendar was modified (formatted RFC 3339 timestamp).")
@attr('account', type=ResourceType(accepted_types=('resources/GoogleAccount',)))
class GoogleCalendar(Device):

    @set_interval(CALENDAR_POLL_INTERVAL, name="GoogleCalendar.poll")
    def _update(self):
        LOGGER.debug('calendar poll')
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self.account.get_calendar_service().events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        LOGGER.debug('calendar result: %s', events_result)

        if not self.description:
            description = events_result.get('description', '')
            if description:
                self.description = description

        events = events_result.get('items', [])
        LOGGER.debug('calendar events: %s', events)

        with self:
            self.events = events
            self.contentModifiedDate = utcnow()

    @method.return_type('object')
    def list_events(self):
        return self.events
