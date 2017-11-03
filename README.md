
e-Thing
=====

![e-Thing diagram](https://cloud.githubusercontent.com/assets/17341216/17180858/1fce5e54-541e-11e6-8e0a-09cc853e4e93.png)

This project is an "Internet of Things" application. Store and retrieve data using HTTP requests from devices such as an [Arduino](https://github.com/e-thing/arduino).
Access remotely to your data and control your devices from anywhere.

This project can easily be installed on a Raspberry Pi or any computer.


## Overview



#### Access your data anywhere

A web client is also provided to browse, view and edit your data, to manage and communicate with your devices.
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
- bluetooth low energy devices
- SSH
- ZigBee (coming soon...)



#### Rules editor

Create custom rules to execute tasks when an event occurs and under certains conditions.
Users can easily create or change any automation process without any previous programing or automation experience.


#### APIs

Many APIs are provided to communicate with the e-Thing server :

- [HTTP API](http://e-thing.github.io/doc/http)
- [Javascript API](http://e-thing.github.io/doc/js)
- [Arduino API](http://e-thing.github.io/doc/arduino.html)

Use these APIs to create your own device !




#### Notification

Notification can also be sent on event. For instance, the user can be notified by email when a device sends
a value greater than a threshold or if it has low battery.



## Installation

- Easy install
 
 ```bash
 sudo ./install.sh
 ```

- Manual install
 
 see [INSTALL.md](INSTALL.md)
 
 
## Configuration

The configuration file **config.json** is located in the root directory. An example is given in `default-config.json`.

* set your mongodb server address here with the correct port number. Default to the local database.

 ```json
 {
     "db": {
        "host": "localhost",
        "port": 27017,
        "user": null,
        "password": null,
        "database": "ething"
     }
 }
 ```
* set the URL-path of the EThing root url. For instance, if EThing is accessible through http://192.168.1.117/path, the value is "/path". Default to "/ething".

 ```json
 {
     "path": "/ething"
 }
 ```
* [optional] change the default password.

 ```json
 {
     "auth": {
        "password": "admin",
        "localonly": false
     }
 }
 ```
* [optional] configure a SMTP server if you want some notification to be sent.

 ```json
 {
     "notification": {
        "emails": [
            "example@gmail.com"
        ],
        "smtp": {
            "host": "smtp.gmail.com",
            "port": 587,
            "user": "example@gmail.com",
            "password": "password"
        }
     }
 }
 ```
* [optional] set proxy settings if needed.

 ```json
 {
     "proxy": {
        "host": "proxy-host",
        "port": 8080,
        "user": null,
        "password": null
     }
 }
 ```
* [optional] enable MQTT.

 ```json
 {
     "mqtt": {
        "host": "localhost",
        "port": 1883
     }
 }
 ```

## Installation check

To check if the installation worked, go to the admin interface [http://&lt;YOUR_SERVER_ADDRESS&gt;/ething/client/#!settings?page=status](http://localhost/ething/client/#!settings?page=status).
Connect with the credentials set in the **config.php** file (default is admin).
In that page, you will see if something is missing.



