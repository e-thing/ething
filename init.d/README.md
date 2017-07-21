
## Install the daemon script (execute command as root)

 ```bash
 cp init.d/ethingd /etc/init.d/
 chmod +x  /etc/init.d/ethingd
 # if necessary, edit /etc/init.d/ethingd to change the ETHING_DIR variable (default: /var/www/html/ething)
 update-rc.d ethingd defaults
 
 service ethingd {start|stop|restart|status}
 ```
 
 