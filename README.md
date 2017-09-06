
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



#### APIs

Many APIs are provided to communicate with the e-Thing server :

- [HTTP API](http://e-thing.github.io/doc/http)
- [Javascript API](http://e-thing.github.io/doc/js)
- [Arduino API](http://e-thing.github.io/doc/arduino.html)

Use these APIs to create your own device !


#### Hardware

Compatible devices:

- any HTTP device
- IP camera with RTSP support
- [MySensors](//www.mysensors.org)
- [RFLink](//rflink.nl)
- custom MQTT
- Denon/Marantz audio receiver (tested on Marantz M-CR611)



#### Notification

Notification can also be sent on event. For instance, the user can be notified by email when a device sends
a value greater than a threshold or if it has low battery.


## Installation

- Install APACHE webserver + PHP

 link: https://www.raspberrypi.org/documentation/remote-access/web-server/apache.md

 ```bash
 sudo apt-get install php5 libapache2-mod-php5
 ```

- Install MongoDB

 ```bash
 sudo apt-get install mongodb
 ```

- Install MongoDB PHP driver

 link: http://php.net/manual/fr/set.mongodb.php

- Install Curl PHP driver

 ```bash
 sudo apt-get install php5-curl
 ```

- Install PHP GD library (optional, used for creating thumbnails)

 ```bash
 sudo apt-get install php5-gd
 ```
 
- Install Python 2.7 & pyserial

 ```bash
 sudo apt-get install python
 sudo apt-get install python-pip
 sudo pip install --upgrade pyserial
 ```

- Install Mosquitto (optional)

 Only if you want enable MQTT.
 
 ```bash
 sudo apt-get install mosquitto
 ```
 
 on Raspberry Pi with WebSocket enabled : https://mosquitto.org/2013/01/mosquitto-debian-repository/
 
 ```bash
 # import the repository package signing key
 wget http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key
 sudo apt-key add mosquitto-repo.gpg.key
 
 # Then make the repository available to apt:
 cd /etc/apt/sources.list.d/
 # Then one of the following, depending on which version of debian you are using:
 sudo wget http://repo.mosquitto.org/debian/mosquitto-jessie.list
 sudo wget http://repo.mosquitto.org/debian/mosquitto-wheezy.list
 
 # install mosquitto
 apt-get update
 apt-get install mosquitto
 ```
 
 Add the following to the configuration file
 
 ```json
 {
     "mqtt": {
         "host": "localhost",
         "port": 1883
     }
 }
 ```

- Install NodeJS

 ```bash
 curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
 sudo apt-get install nodejs
 ```
 
- Go to your web server's document root (e.g., /var/www/html) and download the project package using Git

 ```bash
 git clone https://github.com/e-thing/ething.git
 ```

- Additionally you need to install dependencies using [Composer](https://getcomposer.org/download). Go to the 'ething' folder and execute :

 ```bash
 composer install
 ```

- Install the daemon script (execute command as root)

 ```bash
 cp init.d/ethingd /etc/init.d/
 chmod +x  /etc/init.d/ethingd
 # if necessary, edit /etc/init.d/ethingd to change the ETHING_DIR variable (default: /var/www/html/ething)
 update-rc.d ethingd defaults
 
 service ethingd {start|stop|restart|status}
 ```
 
- Access to the project's homepage through :

 `http://<YOUR_SERVER_ADDRESS>/ething`




 
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



