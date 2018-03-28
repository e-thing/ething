
e-Thing
=====


![e-Thing diagram](https://cloud.githubusercontent.com/assets/17341216/17180858/1fce5e54-541e-11e6-8e0a-09cc853e4e93.png)

This project is an "Internet of Things" application. Store and retrieve data using HTTP requests from devices such as an [Arduino](https://github.com/e-thing/arduino).
Access remotely to your data and control your devices from anywhere.

This project was developped on a Raspberry Pi but should work on any Linux computer.

Written in Python 2.7.

## Overview



#### Access your data anywhere

A web interface is provided to browse, view and edit your data, to manage and communicate with your devices.
Use the online editor to write your own script or application using the [Javascript API](http://e-thing.github.io/doc/js).

![screenshot of the dashboard](https://user-images.githubusercontent.com/17341216/32382863-abc4d784-c0b6-11e7-8c4d-71708fe670d9.PNG)

#### Hardware

Compatible devices/protocols :

- any HTTP device
- IP camera with RTSP support
- [MySensors](//www.mysensors.org)
- [RFLink](//rflink.nl)
- MQTT
- Denon/Marantz audio receiver (tested on Marantz M-CR611)
- Yeelight
- MiHome
- bluetooth low energy devices (coming soon...)
- SSH
- [Zigate](//zigate.fr) (coming soon...)


#### Node-RED

Compatible with [Node-RED](//nodered.org). 
See [ething-node-red repository](//github.com/e-thing/ething-node-red).

#### Script editor

Create JavaScript script to execute custom tasks when an event occurs and under certains conditions.


#### APIs

Many APIs are provided to communicate with the e-Thing server :

- [HTTP API](http://e-thing.github.io/doc/http)
- [Javascript API](http://e-thing.github.io/doc/js)
- [Arduino API](http://e-thing.github.io/doc/arduino.html)

Use these APIs to create your own device !


## Running Ething

### Requirements

 - [Node](//nodejs.org/en/download/package-manager/)
 - Python 2.7
 - MongoDB

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

The web interface is available at `http://localhost:8000`. The default password is `admin`.
The log file is stored in `/var/log`.
The configuration file is stored in `~/.ething`.


