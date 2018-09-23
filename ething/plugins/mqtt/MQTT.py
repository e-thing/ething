# coding: utf-8
from future.utils import string_types, integer_types, iteritems

from ething.core.Device import Device
from ething.core.reg import *
from ething.core.Process import get_process

from jsonpath_rw import jsonpath, parse
import xml.etree.ElementTree as ET

import json
import os
import re


@attr('host', type=String(), description="The host of the MQTT broker to connect to.")
@attr('port', type=Integer(min=0, max=65535), default=1883, description="The port number of the MQTT broker to connect to.")
@attr('auth', type=Nullable(Dict(mapping = OrderedDict([('user', String(allow_empty=False)), ('password', String(allow_empty=False))]))), default=None, description="An object describing the credentials to use.")
@attr('subscription', type=Array(Dict(optionals = ['jsonPath', 'regexp', 'xpath'], mapping = OrderedDict([('name', String(allow_empty=False)), ('topic', String(allow_empty=False)), ('jsonPath', String(allow_empty=False)), ('regexp', String(allow_empty=False)), ('xpath', String(allow_empty=False))])), min_len = 1), default=None)
class MQTT(Device):
    """
    MQTT Device resource representation
    """

    @method.arg('topic', type='string', minLength=1)
    @method.arg('payload', payload='string')
    def publish(self, topic, payload=''):
        return get_process('mqtt.%s' % self.id).publish(topic, payload)

    def processPayload(self, topic, payload):

        payload = payload.decode('utf8')

        for item in self.subscription:

            if item.get('topic') == topic:
                
                name = item.get('name')
                
                if item.get('jsonPath'):

                    json_path = item.get('jsonPath')

                    try:
                        decoded = json.loads(payload)

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
                                    self.store(name, data)
                                    continue

                    except ValueError:
                        pass

                elif item.get('regexp'):

                    regexp = item.get('regexp')

                    rec = re.compile(regexp)
                    data = None

                    for line in payload.splitlines():
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
                        self.store(name, data)
                        continue

                elif item.get('xpath'):

                    xpath = item.get('xpath')

                    try:
                        tree = ET.fromstring(payload)
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
                                self.store(name, data)
                                continue

                self.ething.log.warning(
                    'unable to handle the message from topic %s' % topic)

    def store(self, name, value):
        self.data[name] = value

        try:
            table = self.ething.findOne(lambda r: r.isTypeof('resources/Table') and r.name == name and r.createdBy == self)

            if not table:
                # create it !
                table = self.ething.create('resources/Table', {
                    'name': name,
                    'createdBy': self.id,
                    'maxLength': 5000
                })

            if table:
                table.insert({
                    name: value
                })
        except:
            self.ething.log.exception('history error for %s' % name)