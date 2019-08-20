# coding: utf-8

import os
from subprocess import check_output
import sys
import re
import logging


_LOGGER = logging.getLogger('bluetooth')


def list_bluetooth_interfaces():
    interfaces = []

    if os.name != 'nt':
        # does not work on windows
        try:
            read_status = False
            output = check_output("hciconfig -a", shell=True)
            for line in output.decode(sys.stdout.encoding or 'utf8').splitlines():
                line = line.strip()

                matches = re.search('^(hci[0-9]+):', line)
                if matches:
                    # new block
                    hci = matches.group(1)

                    interfaces.append({
                        'hci': hci
                    })

                    read_status = False
                else:
                    if read_status:
                        read_status = False
                        if len(interfaces) > 0:
                            interfaces[-1]['status'] = line

                    else:
                        matches = re.search('^Name: *[\'"]?([^\'"]*)[\'"]?', line)
                        if matches:
                            name = matches.group(1)
                            if len(interfaces) > 0:
                                interfaces[-1]['name'] = name
                        else:
                            matches = re.search('^BD Address: *([0-9a-fA-F:]+)', line)
                            if matches:
                                read_status = True
                                address = matches.group(1)
                                if len(interfaces) > 0:
                                    interfaces[-1]['address'] = address
                            else:
                                matches = re.search('^Manufacturer: *(.+)$', line)
                                if matches:
                                    manufacturer = matches.group(1).strip()
                                    if len(interfaces) > 0:
                                        interfaces[-1]['manufacturer'] = manufacturer


        except:
            _LOGGER.exception('error in hciconfig')
    
    return interfaces


