# coding: utf-8
from future.utils import string_types, integer_types, iteritems

from ething.Device import Device, method, attr, isString, isInteger, isObject, isNone, PRIVATE

from jsonpath_rw import jsonpath, parse
import xml.etree.ElementTree as ET

import json
import os
import re


@attr('host', validator=isString(), description="The host of the MQTT broker to connect to.")
@attr('port', validator=isInteger(min=0, max=65535), default=1883, description="The port number of the MQTT broker to connect to.")
@attr('auth', validator=isNone() | isObject(user=isString(allow_empty=False), password=isString(allow_empty=False)), default=None, description="An object describing the credentials to use.")
@attr('subscription', mode=PRIVATE, default=None)
class MQTT(Device):
    """
    MQTT Device resource representation
    """

    @method.arg('topic', type='string', minLength=1)
    @method.arg('payload', payload='string')
    def publish(self, topic, payload=''):
        return self.ething.rpc.request('device.mqtt.send', self.id, topic, payload)

    def getSubscription(self):
        spec = self.ething.fs.retrieveFile(self._subscription)
        return json.loads(spec.decode('utf8')) if spec else []

    def setSubscription(self, subs):

        if isinstance(subs, list):
            for v in subs:

                if not isinstance(v, dict):
                    raise ValueError('sub item must be a dictionary')

                if 'topic' not in v:
                    raise ValueError('the key "topic" is mandatory')

                for k, vv in iteritems(v):

                    if k == 'topic':
                        if not isinstance(vv, string_types) or len(vv) == 0:
                            raise Exception(
                                'topic: must be a non empty string')

                    elif k == 'jsonPath':
                        if not isinstance(vv, string_types) and vv is not None:
                            raise Exception('jsonPath: must be a string')

                    elif k == 'regexp':
                        if not isinstance(vv, string_types) and vv is not None:
                            raise Exception('regexp: must be a string')
                    elif k == 'xpath':
                        if not isinstance(vv, string_types) and vv is not None:
                            raise Exception('xpath: must be a string')
                    else:
                        raise Exception('unknown key \'%s\'' % k)

        elif subs is not None:
            raise ValueError('subs must either be None or a list')

        # remove that file if it exists
        self.ething.fs.removeFile(self._subscription)
        self._subscription = None

        if subs:
            self._subscription = self.ething.fs.storeFile('Device/%s/subscription' % self.id, json.dumps(subs).encode('utf8'), {
                'parent': self.id
            })

        self.save()

        return True

    def processPayload(self, topic, payload):

        for item in self.getSubscription():

            if item.get('topic') == topic:

                json_path = item.get('jsonPath')

                if item.get('jsonPath'):

                    json_path = item.get('jsonPath')

                    try:
                        decoded = json.loads(payload.decode('utf8'))

                        try:
                            jsonpath_expr = parse(json_path)
                        except Exception:
                            pass
                        else:
                            results = [
                                match.value for match in jsonpath_expr.find(decoded)]
                            if len(results):
                                data = results[0]

                                if isinstance(data, integer_types) or isinstance(data, float) or isinstance(data, string_types) or isinstance(data, bool):
                                    self.store(os.path.basename(
                                        topic), {'value': data})
                                    continue

                    except ValueError:
                        pass

                elif item.get('regexp'):

                    regexp = item.get('regexp')

                    rec = re.compile(regexp)
                    data = None

                    for line in payload.decode('utf8').splitlines():
                        matches = rec.search(line)
                        if matches:
                            data = matches.group(1) if len(
                                matches.groups()) > 0 else matches.group(0)

                            try:
                                data = float(data)
                            except ValueError:
                                pass

                            break

                    if data is not None:
                        self.store(os.path.basename(topic), {'value': data})
                        continue

                elif item.get('xpath'):

                    xpath = item.get('xpath')

                    try:
                        tree = ET.fromstring(payload.decode('utf8'))
                        elements = [r.text for r in tree.findall(xpath)]
                    except Exception:
                        pass
                    else:

                        if len(elements) > 0:
                            data = elements[0]

                            try:
                                data = float(data)
                            except ValueError:
                                pass

                            if isinstance(data, integer_types) or isinstance(data, float) or isinstance(data, string_types) or isinstance(data, bool):
                                self.store(os.path.basename(
                                    topic), {'value': data})
                                continue

                self.ething.log.warning(
                    'unable to handle the message from topic %s' % topic)
