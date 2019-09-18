# coding: utf-8

from ething.plugin import Plugin
from ething.reg import *
from ething import Device
from ething.utils.date import TzDate, utcnow
from ething.scheduler import set_interval

from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

import logging
import pickle


LOGGER = logging.getLogger(__name__)


ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'

AUTHORIZATION_SCOPE ='openid email profile https://www.googleapis.com/auth/calendar.readonly'

AUTH_STATE_KEY = 'auth_state'
USERS_KEY = 'google_users'

CALENDAR_POLL_INTERVAL = 60


class GoogleUserNotLoggedException(Exception):
    pass

@attr('client_secret', label="client secret", type=String(), default='')
@attr('client_id', label="client id", type=String(), default='')
class Google(Plugin):

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

    def _webserver_install(self):

        # install specific http routes
        webserver_plugin = self.core.plugins['webserver']
        if not webserver_plugin:
            return

        app = webserver_plugin.app
        auth = app.auth

        from flask import request, redirect, url_for, session

        @app.route('/api/google/login')
        @auth.required()
        def login():
            if not self.client_id or not self.client_secret:
                raise Exception('no client_id or client_secret set')

            redirect_uri = re.sub('/api/google/login.*$', '/api/google/auth', request.url)

            LOGGER.debug('google/login client_id=%s client_secret=%s scope=%s redirect_uri=%s', self.client_id, self.client_secret, AUTHORIZATION_SCOPE, redirect_uri)

            oauth2_session = OAuth2Session(self.client_id, self.client_secret, scope=AUTHORIZATION_SCOPE, redirect_uri=redirect_uri)

            uri, state = oauth2_session.create_authorization_url(AUTHORIZATION_URL)

            LOGGER.debug('google/login uri=%s, state=%s', uri, state)

            self.session[AUTH_STATE_KEY] = state

            return redirect(uri, code=302)

        @app.route('/api/google/auth')
        @auth.required()
        def google_auth_redirect():

            if not self.client_id or not self.client_secret:
                raise Exception('no client_id or client_secret set')

            req_state = request.args.get('state', default=None, type=None)

            if req_state != self.session[AUTH_STATE_KEY]:
                raise Exception('Invalid state parameter')

            redirect_uri = re.sub('/api/google/auth.*$', '/api/google/auth', request.url)

            LOGGER.debug('google/auth client_id=%s client_secret=%s scope=%s redirect_uri=%s state=%s', self.client_id,
                         self.client_secret, AUTHORIZATION_SCOPE, redirect_uri, self.session[AUTH_STATE_KEY])

            oauth2_session = OAuth2Session(self.client_id, self.client_secret,
                                    scope=AUTHORIZATION_SCOPE,
                                    state=self.session[AUTH_STATE_KEY],
                                    redirect_uri=redirect_uri)

            oauth2_tokens = oauth2_session.fetch_access_token(
                ACCESS_TOKEN_URI,
                authorization_response=request.url)

            LOGGER.debug('google/auth oauth2_tokens=%s', oauth2_tokens)

            # fetch user information
            credentials = self._build_credentials(oauth2_tokens)
            oauth2_client = googleapiclient.discovery.build(
                'oauth2', 'v2',
                credentials=credentials)

            user_info = oauth2_client.userinfo().get().execute()

            LOGGER.debug('google/auth user_info=%s', user_info)

            self._add_user(user_info, oauth2_tokens)

            return redirect(url_for('root_client'), code=302)

        @app.route('/api/google/logout/<user_id>')
        @auth.required()
        def logout(user_id):
            LOGGER.debug('google/logout')
            self._remove_user(user_id)
            return '', 204

        @app.route('/api/google/users')
        @auth.required()
        def list_users():
            return app.jsonify(self.users)

    def _build_credentials(self, oauth2_tokens):
        if not self.client_id or not self.client_secret:
            raise Exception('no client_id or client_secret set')

        if isinstance(oauth2_tokens, string_types): # user id
            oauth2_tokens = self.find_user(oauth2_tokens)

        if isinstance(oauth2_tokens, GoogleUser): # user instance
            oauth2_tokens = oauth2_tokens.tokens

        if not oauth2_tokens:
            raise Exception('not logged in')

        return google.oauth2.credentials.Credentials(
            oauth2_tokens['access_token'],
            refresh_token=oauth2_tokens['refresh_token'],
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_uri=ACCESS_TOKEN_URI)

    def _add_user(self, user_info, oauth2_tokens):

        user = GoogleUser(user_info, oauth2_tokens)

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
            raise GoogleUserNotLoggedException()

    def get_calendar_service(self, user):
        credentials = self._build_credentials(user)
        return googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    def get_calendar_default_attributes(self, user):
        service = self.get_calendar_service(user)
        result = service.calendars().get(calendarId='primary').execute()
        description = result.get('description', '')
        summary = result.get('summary', '')

        ret = {}

        if description:
            ret['description'] = description
        if summary:
            ret['name'] = summary

        return ret


class GoogleUser(object):

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
        if isinstance(other, GoogleUser):
            return self.id == other.id
        elif isinstance(other, string_types):
            return self.id == other
        else:
            return False

    def __json__(self):
        return self._user_info


class GoogleUserType(String):
    def __init__(self, **attr):
        super(GoogleUserType, self).__init__(allow_empty=False, **attr)

    def to_shema(self, context = None):
        s = super(GoogleUserType, self).to_shema(context)
        s['$component'] = 'GoogleUserForm'
        return s


@attr('user', type=GoogleUserType())
class GoogleBaseDevice(Device):

    @property
    def _plugin(self):
        return self.core.plugins['google']

    @property
    def user_obj(self):
        return self._plugin.find_user(self.user)


# https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/calendar_v3.events.html#list

@meta(icon="mdi-calendar")
@attr('events', mode=PRIVATE, default=[])
@attr('contentModifiedDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY, description="Last time the content of this calendar was modified (formatted RFC 3339 timestamp).")
class GoogleCalendar(GoogleBaseDevice):

    @classmethod
    def __instantiate__(cls, data, data_src, context):
        if not data.get('description'):
            defaults = context['core'].plugins['google'].get_calendar_default_attributes(data['user'])
            if defaults.get('description'):
                data['description'] = defaults['description']
        return super(GoogleCalendar, cls).__instantiate__(data, data_src, context)

    @property
    def _service(self):
        return self._plugin.get_calendar_service(self.user)

    @set_interval(CALENDAR_POLL_INTERVAL, name="GoogleCalendar.poll")
    def _update(self):
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self._service.events().list(calendarId='primary', timeMin=now,
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

    @method
    def list_events(self):
        return self.events
