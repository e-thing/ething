#!/bin/sh


INTERACTIVE=""

if ! [ $(id -u) = 0 ]; then
   echo "ERROR: This script must be run as root" 1>&2
   exit 1
fi


echo
echo "# Installing EThing"
echo

for p in grep awk lsb_release curl apt-get readlink dirname uname update-rc.d wget service sed
do
	type "$p" > /dev/null 2>&1
	if [ $? -ne 0 ] ; then
		echo "ERROR: unable to execute '$p'" 1>&2
		exit 1
	fi
done


SYSNAME=$(uname -s) # Linux
CODENAME=$(lsb_release -c | awk '{print $NF;}')
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

echo "System information :"
echo "system=${SYSNAME}"
echo "distribution=${CODENAME}"
echo "directory=${SCRIPTPATH}"
echo

if [ "${CODENAME}" != "stretch" ] && [ "${CODENAME}" != "wheezy" ] && [ "${CODENAME}" != "jessie" ] ; then
	echo "WARNING: the version of your distribution is not among the following: stretch, wheezy, jessie" 1>&2
fi



echo "## apt-get update ..."
apt-get update
echo


echo "## installing apache web server ..."
apt-get install ${INTERACTIVE} apache2
type apache2 a2enmod a2enconf apachectl
apacheErr=$?
if [ ${apacheErr} -eq 0 ] ; then
	# sucessful installation
	
	apachectl -V
	
	a2enmod rewrite

	apacheDir=/etc/apache2
	if [ -d "${apacheDir}" ] ; then

		confFile=${apacheDir}/conf-available/ething.conf

		cat <<EOF > ${confFile}

<Directory "${SCRIPTPATH}">
	# enable .htaccess
	AllowOverride ALL
</Directory>

EOF

		a2enconf ething

		siteFile=${apacheDir}/sites-available/000-default.conf
		if [ -s "${siteFile}" ] ; then
			if [ $(grep -c "ething.conf" "${siteFile}") -eq 0 ] ; then
				cp -p "${siteFile}" "${siteFile}.save"
				sed -i 's/<\/VirtualHost>/  Include conf-available\/ething.conf\n<\/VirtualHost>/' "${siteFile}"
			else
				echo "INFO: apache default site '${siteFile}' already configured"
			fi
			
			echo "INFO: apache is successfully installed"
		else
			apacheErr="unable to find the apache default site conf '${siteFile}'"
			echo "ERROR: ${apacheErr}" 1>&2
		fi

	else
		apacheErr="unable to find the apache directory '${apacheDir}'"
		echo "ERROR: ${apacheErr}" 1>&2
	fi
else
	echo "ERROR: unable to install apache web server" 1>&2
	exit 1
fi
echo

echo "## installing PHP ..."
apt-get install ${INTERACTIVE} php5 php-pear php5-dev libapache2-mod-php5 php5-curl php5-gd libssh2-1-dev
type php pecl
phpErr=$?
if [ ${phpErr} -eq 0 ] ; then
	php -v
	
	if [ $(php -m | grep -c ssh2) -eq 0 ] ; then
		pecl install ssh2
		phpErr=$?
		if [ ${phpErr} -ne 0 ] ; then
			phpErr="unable to install ssh2 PHP extension"
			echo "ERROR: ${phpErr}" 1>&2
		fi
	else
		echo "INFO: ssh2 PHP extension already installed"
	fi
	
	if [ $(php -m | grep -c mongodb) -eq 0 ] ; then
		pecl install mongodb
		phpErr=$?
		if [ ${phpErr} -ne 0 ] ; then
			echo "ERROR: unable to install mongodb PHP extension" 1>&2
			exit 1
		fi
	else
		echo "INFO: mongodb PHP extension already installed"
	fi
	
	if [ ${phpErr} -eq 0 ] ; then
		echo "INFO: PHP is successfully installed"
	fi
else
	echo "ERROR: unable to install PHP" 1>&2
	exit 1
fi
echo

echo "## installing mongodb ..."
apt-get install ${INTERACTIVE} mongodb
type mongo
mongoErr=$?
if [ ${mongoErr} -eq 0 ] ; then
	mongo --version
	echo "INFO: mongodb is successfully installed"
else
	echo "ERROR: unable to install mongodb" 1>&2
	exit 1
fi
echo

echo "## installing python ..."
apt-get install ${INTERACTIVE} python python-pip python-dev build-essential
pip install pyserial || exit 1
type python
pythonErr=$?
if [ ${pythonErr} -eq 0 ] ; then
	python -V
	echo "INFO: python is successfully installed"
else
	echo "ERROR: unable to install python" 1>&2
	exit 1
fi
echo

echo "## installing avconv ..."
apt-get install ${INTERACTIVE} libav-tools
type avconv
avconvErr=$?
if [ ${avconvErr} -eq 0 ] ; then
	avconv -version
	echo "INFO: avconv is successfully installed"
else
	echo "ERROR: unable to install avconv" 1>&2
fi
echo

echo "## installing NodeJS ..."
type node
nodejsErr=$?
if [ ${nodejsErr} -ne 0 ] ; then
	wget -qO- https://deb.nodesource.com/setup_8.x | bash -
	type node
	nodejsErr=$?
	if [ ${nodejsErr} -eq 0 ] ; then
		node --version
		echo "INFO: NodeJS is successfully installed"
	else
		echo "ERROR: unable to nodejs" 1>&2
		exit 1
	fi
else
	echo "INFO: nodejs already installed"
fi
echo

echo "## installing Composer ..."
type composer 2> /dev/null
composerErr=$?
type php 2> /dev/null 2>&1
if [ ${composerErr} -ne 0 ] ; then
	php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
	php -r "if (hash_file('SHA384', 'composer-setup.php') === '544e09ee996cdf60ece3804abc52599c22b1f40f4323403c44d44fdfdd586475ca9813a858088ffbc1f233e9b180f061') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;"
	php composer-setup.php
	php -r "unlink('composer-setup.php');"
	type composer
	composerErr=$?
	if [ ${composerErr} -eq 0 ] ; then
		composer --version
		echo "INFO: composer is successfully installed"
	else
		echo "ERROR: unable to install composer" 1>&2
		exit 1
	fi
else
	echo "INFO: composer already installed"
fi
echo


if [ ${composerErr} -eq 0 ] ; then
	echo "## installing dependencies [composer] ..."
	composer install --no-plugins --no-scripts || exit 1
	echo
fi


echo "## installing MQTT ..."
type mosquitto 2> /dev/null
mosquittoErr=$?
if [ ${mosquittoErr} -ne 0 ] ; then
	wget http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key
	apt-key add mosquitto-repo.gpg.key
	rm -f mosquitto-repo.gpg.key
	# Then make the repository available to apt:
	cd /etc/apt/sources.list.d/
	sudo wget "http://repo.mosquitto.org/debian/mosquitto-${CODENAME}.list"
	cd -
	# install mosquitto
	apt-get install mosquitto

	# <!> if your are on stretch, you may need to install the following dependencies manually (libssl & libwebsockets)
	#wget http://security.debian.org/debian-security/pool/updates/main/o/openssl/libssl1.0.0_1.0.1t-1+deb8u6_armhf.deb
	#dpkg -i libssl1.0.0_1.0.1t-1+deb8u6_armhf.deb
	#rm -f libssl1.0.0_1.0.1t-1+deb8u6_armhf.deb
	#wget http://ftp.nz.debian.org/debian/pool/main/libw/libwebsockets/libwebsockets3_1.2.2-1_armhf.deb
	#dpkg -i libwebsockets3_1.2.2-1_armhf.deb
	#rm -f libwebsockets3_1.2.2-1_armhf.deb
	#apt-get install mosquitto
	
	type mosquitto
	mosquittoErr=$?
	
	if [ ${mosquittoErr} -eq 0 ] ; then
		
		#Enabling websockets :
		mosquittoConfDir=/etc/mosquitto/conf.d
		wsconf=${mosquittoConfDir}/websocket.conf
		if [ -d "${mosquittoConfDir}" ] ; then
			if [ -s "${wsconf}" ] ; then
				cp -p "${wsconf}" "${wsconf}.save"
			fi
			
			cat <<EOF > ${wsconf}
listener 1883
listener 1884
protocol websockets
EOF
			
			mosquittoInstalled=1
			echo "INFO: mosquitto is successfully installed"
			
		else
			mosquittoErr="unable to find the mosquitto directory '${mosquittoConfDir}'"
			echo "ERROR: ${mosquittoErr}" 1>&2
		fi
	else
		mosquittoErr="unable to install mosquitto"
		echo "ERROR: ${mosquittoErr}" 1>&2
	fi
	
else
	echo "INFO: mosquitto already installed"
fi
if [ ${mosquittoErr} -eq 0 ] ; then
	# Enable Mosquitto autostart on boot :
	update-rc.d mosquitto defaults
fi
echo


echo "## installing the daemon script ..."
cat ${SCRIPTPATH}/init.d/ethingd | sed 's@^ETHING_DIR=.*$@ETHING_DIR="'${SCRIPTPATH}'"@' > /etc/init.d/ethingd
chmod +x  /etc/init.d/ethingd
update-rc.d ethingd defaults
echo


echo "## configure ething ..."
config=${SCRIPTPATH}/config.json
if [ -s " ${config}" ] ; then
	cp -p  "${config}" "${config}.save"
else
	echo "{}" > ${config}
fi
if [ -n "${mosquittoInstalled}" ] && [ "${mosquittoInstalled}" -eq 1 ]; then
	php -r "echo json_encode(array_merge(json_decode(file_get_contents('./config.json'), true), json_decode('{\"mqtt\": {\"host\": \"localhost\"}}', true)));" > ${config}
fi
echo

echo "## apache restart ..."
systemctl restart apache2
echo

echo "## mosquitto restart ..."
service mosquitto restart
echo

echo "## start ething daemon ..."
service ethingd restart
echo


echo "## status: "
php ${SCRIPTPATH}/tools/check.php



if [ ${apacheErr} -ne 0 ] || [ ${phpErr} -ne 0 ] || [ ${mongoErr} -ne 0 ] || [ ${pythonErr} -ne 0 ] || [ ${avconvErr} -ne 0 ] || [ ${nodejsErr} -ne 0 ] || [ ${composerErr} -ne 0 ] || [ ${mosquittoErr} -ne 0 ] ; then
	echo "ERROR: there were errors during installation" 1>&2
	exit 2
fi


exit 0
