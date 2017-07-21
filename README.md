
e-Thing
=====

![e-Thing diagram](https://cloud.githubusercontent.com/assets/17341216/17180858/1fce5e54-541e-11e6-8e0a-09cc853e4e93.png)

This project is an "Internet of Things" application. Store and retrieve data using HTTP requests from devices such as an [Arduino](https://github.com/e-thing/arduino).
Access remotely to your data and control your devices from anywhere.

This project can easily be installed on a Raspberry Pi or any computer.


## Overview


#### Access your data anywhere

A web client is also provided to browse, view and edit your data, to manage and communicate with your devices.
Use the online editor to write your own application using the [Javascript API](http://e-thing.github.io/doc/js).

![ething_screenshot](https://cloud.githubusercontent.com/assets/17341216/17768812/20bf8e22-6536-11e6-8bdf-dfadbc171fb1.jpg)

#### APIs

Many APIs are provided to communicate with the e-Thing server :

- [HTTP API](http://e-thing.github.io/doc/http)
- [Javascript API](http://e-thing.github.io/doc/js)
- [Arduino API](http://e-thing.github.io/doc/arduino.html)

Use these APIs to create your own device !

#### Connect your devices

- client mode :
A device can access to the data from the e-Thing server :
 - write access : e.g. a device sending the temperature at regular intervals. Devices can store data in a table or in a file, such as text or binary data (image for instance).
 - read access : e.g. a device reading the temperature from a distant thermometer and turn on a fan when the value is above a threshold.

- server mode :
A device can also be accessed from the web client, e.g. switch on/off a led.
The device act like a server listening to incoming HTTP requests.
To activate this mode, you must provide the URL of the device and a [Swagger specification](http://swagger.io).
The Swagger specification describes the available requests that your device accepts. 

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

 ```bash
 sudo apt-get install mosquitto
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

The configuration file **config.php** is located in the root directory.

* set your mongodb server address here with the correct port number.
* [optional] change the default password.
* [optional] configure a SMTP server if you want some notification to be sent.
* [optional] set proxy settings if needed.


## Installation check

To check if the installation worked, go to the admin interface [http://&lt;YOUR_SERVER_ADDRESS&gt;/ething/client/#!settings?page=status](http://localhost/ething/client/#!settings?page=status).
Connect with the credentials set in the **config.php** file (default is admin).
In that page, you will see if something is missing.



