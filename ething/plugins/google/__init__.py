# coding: utf-8

from ething.plugin import Plugin, PluginSignal
from ething.db import *
from ething import Device
from ething.utils.date import TzDate, utcnow
from ething.scheduler import set_interval
from ething.utils import deep_eq

from authlib.integrations.requests_client import OAuth2Session
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


class GoogleCalendarUpdated(PluginSignal):
    """
    is emitted each time a the google calendar has been updated
    """
    pass


@throw(GoogleCalendarUpdated)
class Google(Plugin):

    JS_INDEX = './js/index.js'

    def load(self):
        self.session = dict()
        self.calendar_events = []

    def setup(self):

        # install specific http routes
        self._webserver_install()

    @set_interval(CALENDAR_POLL_INTERVAL, name="GoogleCalendar.poll")
    def _update_calendar(self):
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        accounts = self.core.db.os.find(GoogleAccount)

        events = []
        for account in accounts:
            events_result = account.get_calendar_service().events().list(calendarId='primary', timeMin=now,
                                                                              maxResults=10, singleEvents=True,
                                                                              orderBy='startTime').execute()
            events += events_result.get('items', [])

        LOGGER.debug('calendar events: %s', events)

        prev_events = self.calendar_events

        if deep_eq(events, prev_events):
            self.emit(GoogleCalendarUpdated(self))

        self.calendar_events = events

    @method.return_type('object')
    def list_calendar_events(self):
        return self.calendar_events

    def _webserver_install(self):

        # install specific http routes

        app = self.core.plugins['webserver'].app
        auth = app.auth

        from flask import request, redirect, url_for, Response

        @app.route('/api/google/login')
        @auth.required()
        def google_login():
            account = self.core.db.os.get(GoogleAccount, request.args.get('account')) # account id
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

            account.token = dict(oauth2_tokens)

            account.fetch_user_info()

            return redirect(url_for('root_client'), code=302)

        @app.route('/api/google/accounts')
        @auth.required()
        def list_accounts():
            return app.jsonify(self.core.db.os.find(GoogleAccount))

        @app.route('/api/google/accounts', methods=['POST'])
        @auth.required()
        def create_account():
            attr = request.get_json()

            if isinstance(attr, dict):
                account = self.core.db.os.create(GoogleAccount, attr)

                if account:
                    response = app.jsonify(account)
                    response.status_code = 201
                    return response
                else:
                    raise Exception('Unable to create the account')

            raise Exception('Invalid request')

        @app.route('/api/google/accounts/<id>', methods=['DELETE'])
        @auth.required()
        def delete_account(id):
            account = self.core.db.os.get(GoogleAccount, id)
            if account:
                remove(account)
                return '', 204
            else:
                raise Exception('Not found')

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
@attr('user', mode=READ_ONLY, default={})
@attr('client_secret', label="client secret", type=String(allow_empty=False), mode=CREATE_ONLY_PRIVATE)
@attr('client_id', label="client id", type=String(allow_empty=False), mode=CREATE_ONLY_PRIVATE)
@attr('name', type=String(allow_empty=False), description="an arbitrary name for that account")
@uid()
@meta(icon="mdi-google", description="""
1. Go to the [Google API Console](https://console.developers.google.com)
2. Select a project, or create a new one.
3. On the Credentials page, select **Create credentials**, then **OAuth client ID**.
4. Under **Application type**, choose **Web application**.
5. Under Authorized redirect URIs, add a line with:
```
# replace <ething-server-ip> by the ip address of your ething server.
http://<ething-server-ip>:8000/api/google/auth
```
6.  Click  **Create**.
7.  On the page that appears, take note of the  **client ID**  and  **client secret**.""")
@db(table='googleaccounts')
class GoogleAccount(Entity):

    def __init__(self, *args, **kwargs):
        super(GoogleAccount, self).__init__(*args, **kwargs)
        self.oauth = OAuth2Session(self.client_id, self.client_secret, scope=AUTHORIZATION_SCOPE, token=self.token)

    @attr()
    def logged(self):
        return bool(self.token)

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

    def fetch_user_info(self):
        # fetch user information
        oauth2_client = googleapiclient.discovery.build(
            'oauth2', 'v2',
            credentials=self._build_credentials())

        user_info = oauth2_client.userinfo().get().execute()
        self.user = dict(user_info)

    def get_calendar_service(self):
        return googleapiclient.discovery.build('calendar', 'v3', credentials=self._build_credentials())


class GoogleUserType(String):
    def __init__(self, **attr):
        super(GoogleUserType, self).__init__(allow_empty=False, **attr)

    def to_shema(self, context = None):
        s = super(GoogleUserType, self).to_shema(context)
        s['$component'] = 'GoogleUserForm'
        return s

    def set(self, value, context=None):
        if isinstance(value, GoogleAccount):
            value = value.id
        return super(GoogleUserType, self).set(value, context)

    def get(self, value, context=None):
        return context['core'].db.os.get(GoogleAccount, value)


@abstract
@attr('account', type=GoogleUserType())
class GoogleBaseDevice(Device):
    pass

# # deprecated (moved in plugin)
# @meta(icon="mdi-calendar")
# @attr('events', mode=PRIVATE, default=[])
# @attr('contentModifiedDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY, description="Last time the content of this calendar was modified (formatted RFC 3339 timestamp).")
# class GoogleCalendar(GoogleBaseDevice):
#
#     @set_interval(CALENDAR_POLL_INTERVAL, name="GoogleCalendar.poll")
#     def _update(self):
#         now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
#         events_result = self.account.get_calendar_service().events().list(calendarId='primary', timeMin=now,
#                                               maxResults=10, singleEvents=True,
#                                               orderBy='startTime').execute()
#
#         if not self.description:
#             description = events_result.get('description', '')
#             if description:
#                 self.description = description
#
#         events = events_result.get('items', [])
#         LOGGER.debug('calendar events: %s', events)
#
#         with self:
#             self.events = events
#             self.contentModifiedDate = utcnow()
#
#     @method.return_type('object')
#     def list_events(self):
#         return self.events
