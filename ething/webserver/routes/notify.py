# coding: utf-8

from flask import request, Response
from ..server_utils import *


def install(core, app, auth, **kwargs):

    notify_args = {
        'subject': fields.Str(required=True, location="json"),
        'body': fields.Str(location="json"),
    }

    @app.route('/api/notification', methods=['POST'])
    @auth.required('notification')
    @use_args(notify_args)
    def notify(args):
        """
        ---
        post:
          description: Send a notification to the registered email addresses (cf. settings).
          parameters:
            - name: notification data
              in: body
              description: the data of the notification to be sent
              required: true
              schema:
                type: object
                properties:
                  subject:
                    type: string
                    description: the subject of the notification (default to 'notification')
                  body:
                    type: string
                    description: the content of the notification
          responses:
            '200':
              description: The notification was successfully sent
        """
        core.notify(args['subject'], args['body'])
