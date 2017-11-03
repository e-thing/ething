## Installation

- Install APACHE webserver
 
 ```bash
 # apache
 sudo apt-get install apache2
 
 # enabling apache rewrite module
 sudo a2enmod rewrite
 ```
 
 You also need a directory directive to enable .htaccess files and allow the RewriteEngine directive to be used.
 Edit the file /etc/apache2/sites-available/000-default.conf and modify the virtualhost configuration as following :
 
 ```
 <VirtualHost *:80>
   
   # add the following lines :
   <Directory "/var/www/html">
     AllowOverride ALL
   </Directory>
   
 </VirtualHost>
 ```
 
 Restart apache
 
 ```bash
 sudo systemctl restart apache2
 ```
 
 Optionnaly, change the owner of the apache directory
 
 ```bash
 # change pi by your user name
 sudo chown -R pi: /var/www/html
 ```
 
- Install php5

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
 
- Install SSH2 for PHP (used by SSH device)
 
 For more details, see http://php.net/manual/en/ssh2.installation.php
 
 using PECL :
 
 ```bash
 sudo apt-get install libssh2-1-dev
 sudo pecl install ssh2
 ```
 
 Do not forget to add `extension=ssh2.so` to your php.ini file and to restart apache.
 
- Install Python 2.7 & pyserial

 ```bash
 sudo apt-get install python
 sudo apt-get install python-pip
 sudo pip install --upgrade pyserial
 ```
 
- Install NodeJS

Necessary for executing JavaScript scripts server side.

 ```bash
 curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
 sudo apt-get install nodejs
 ```

- Go to your web server's document root (e.g., /var/www/html) and download the project package using Git

 ```bash
 git clone https://github.com/e-thing/ething.git
 ```
 
 create an empty config file and set the permissions
 
 ```bash
 echo "{}" > config.json
 sudo chown pi:www-data config.json # change pi by your user name
 chmod g+w config.json
 ```
 

- Additionally you need to install the dependencies using [Composer](https://getcomposer.org/download). Go to the 'ething' folder and execute :

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



- Install MQTT server (optional but recommended)

 Installing a MQTT server with websockets support is recommended. MQTT websockets are used by the web client interface for dynamic updates.

 On Raspberry Pi, there is mosquitto with WebSocket enabled : https://mosquitto.org/2013/01/mosquitto-debian-repository/
 
 ```bash
 # import the repository package signing key
 wget http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key
 sudo apt-key add mosquitto-repo.gpg.key
 
 # Then make the repository available to apt:
 cd /etc/apt/sources.list.d/
 # Then one of the following, depending on which version of debian you are using (type the command "lsb_release -a" to get your version)
 sudo wget http://repo.mosquitto.org/debian/mosquitto-stretch.list
 sudo wget http://repo.mosquitto.org/debian/mosquitto-jessie.list
 sudo wget http://repo.mosquitto.org/debian/mosquitto-wheezy.list
 
 # install mosquitto
 sudo apt-get update
 sudo apt-get install mosquitto
 
 # <!> if your are on stretch, you may need to install the following dependencies manually (libssl & libwebsockets)
 wget http://security.debian.org/debian-security/pool/updates/main/o/openssl/libssl1.0.0_1.0.1t-1+deb8u6_armhf.deb
 sudo dpkg -i libssl1.0.0_1.0.1t-1+deb8u6_armhf.deb
 wget http://ftp.nz.debian.org/debian/pool/main/libw/libwebsockets/libwebsockets3_1.2.2-1_armhf.deb
 sudo dpkg -i libwebsockets3_1.2.2-1_armhf.deb
 sudo apt-get install mosquitto
 ```
 
 Enabling websockets :
 in /etc/mosquitto/conf.d/websocket.conf add the following lines:
 
 ```
 listener 1883
 listener 1884
 protocol websockets
 ```
 
 Then restart Mosquitto :
 
 ```bash
 sudo service mosquitto restart
 ```
 
 Enable Mosquitto autostart on boot :
 
 ```bash
 sudo update-rc.d mosquitto defaults
 ```
 
 Add the following to the configuration file 
 
 ```json
 {
     "mqtt": {
         "host": "localhost",
         "port": 1883,
         "user": null,
         "password": null
     }
 }
 ```

If you set a password or set a hostname other than "localhost" or set a different port number, do not forget to update the `client/config.json` file too.



 