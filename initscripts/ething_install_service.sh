#!/bin/sh

# must be run as root


service_file=/lib/systemd/system/ething.service


cat <<EOF > ${service_file}
[Unit]
Description=lancement deamon ething
After=multi-user.target

[Service]
Type=simple
ExecStart=ething
Restart=on-failure
RestartSec=20

[Install]
WantedBy=multi-user.target

EOF


if [ -s ${service_file} ] ; then
	chmod 644 ${service_file}
	systemctl daemon-reload
	systemctl enable ething.service 
	systemctl start ething.service
	systemctl status ething.service
	
	echo "success"
else
	echo "ERROR: unable to create service (must be run as root)"
	exit 1
fi
