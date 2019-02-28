
e-Thing
=====


![e-Thing diagram](https://cloud.githubusercontent.com/assets/17341216/17180858/1fce5e54-541e-11e6-8e0a-09cc853e4e93.png)

This project is an "Internet of Things" application written in Python.
Access remotely to your data and control your devices from anywhere.

This project was developped on a Raspberry Pi but should work on any computer with Python installed.


## Overview


#### Access your data anywhere

A web interface is provided to browse, view and edit your data, to manage and communicate with your devices at `http://localhost:8000`..


#### Hardware

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


#### Node-RED

Compatible with [Node-RED](//nodered.org). 
See [ething-node-red repository](//github.com/e-thing/ething-node-red).

#### Flow editor

Create flow to execute custom tasks when an event occurs and under certains conditions.


#### APIs

Many APIs are provided to communicate with the e-Thing server :

- [HTTP API](https://github.com/e-thing/ething/blob/master/doc/http_api.md)
- [Javascript API](https://github.com/e-thing/ething-js)

Use these APIs to create your own device !


## Running Ething

### Requirements

 - Python 2.7 or >= 3.4

### Installation

```bash
git clone https://github.com/e-thing/ething
cd ething
python setup.py install
```


### Launch

```bash
ething [--daemon]
```

The --daemon argument will start the process as a daemon.

The web interface is available at `http://localhost:8000`. The default login is `ething` and the default password is `admin`.
The log file and the database are stored in `~/.ething` (on windows: `C:\Users\<username>\.ething`).

