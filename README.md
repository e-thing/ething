e-Thing
=======

[![Build Status](https://travis-ci.org/e-thing/ething.svg?branch=master)](https://travis-ci.org/e-thing/ething)
[![Coverage Status](https://coveralls.io/repos/github/e-thing/ething/badge.svg?branch=master)](https://coveralls.io/github/e-thing/ething?branch=master)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/e-thing/ething/graphs/commit-activity)
[![Documentation Status](https://readthedocs.org/projects/ansicolortags/badge/?version=latest)](http://ething.readthedocs.io/)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)







![e-Thing diagram](https://cloud.githubusercontent.com/assets/17341216/17180858/1fce5e54-541e-11e6-8e0a-09cc853e4e93.png)

This project is an "Internet of Things" application written in Python.
Access remotely to your data and control your devices from anywhere.

This project was developped on a Raspberry Pi but should work on any computer with Python installed.

The full documentation can be found at http://ething.readthedocs.io .


## Overview


### Hardware

Compatible devices/protocols :

- IP camera with RTSP support
- [MySensors](//www.mysensors.org)
- [RFLink](//rflink.nl)
- MQTT
- Denon/Marantz audio receiver (tested on Marantz M-CR611)
- Yeelight
- MiHome
- bluetooth low energy devices
- SSH
- [Zigate](//zigate.fr) (coming soon...)

### Flow editor

Create flow to execute custom tasks when an event occurs and under certains conditions.


### Node-RED

Compatible with [Node-RED](//nodered.org). 
See [ething-node-red repository](//github.com/e-thing/ething-node-red).



## Requirements

 - Python >= 3.4 (Python 2.7 should also work)

## Installation

```bash
git clone https://github.com/e-thing/ething
cd ething
python setup.py install
```


## Run

```bash
ething [--daemon]
```

The --daemon argument will start the process as a daemon.

The log file and the database are stored in `~/.ething` (on windows: `C:\Users\<username>\.ething`).


## Web interface

Access your data anywhere. A web interface is provided to browse, view and edit your data, to manage and communicate with your devices.

The web interface is available at `http://localhost:8000`. The default login is `ething` and the default password is `admin`.

To change the port:

```bash
ething --server-port=4000
```

To change the login and password, go under the settings page of the web interface.
