
# BLEA daemon
------------------

Forked from https://github.com/jeedom/plugin-blea

Created by sarakha63. http://sarakha63-domotique.fr/blea-plugin-bluetooth-jeedom/

Based on the bluepy library https://github.com/IanHarvey/bluepy

Modified to be compatible with other controller.

Connect to the daemon using a TCP connection on port 5005.


## installation

Run install.sh with sudo privileges.

```bash
sudo ./install.sh
```

Then lauch the process (you may change the device name depending on your bluetooth device).

```bash
sudo python ./blead.py --device hci0
```

The daemon is now listening on port 5005.

## usage

```
usage: blead.py [-h] --device DEVICE
                [--loglevel {info,notice,none,warning,critical,error,debug}]
                [--port PORT] [--daemonname DAEMONNAME]

Blead Daemon

optional arguments:
  -h, --help            show this help message and exit
  --device DEVICE       Bluetooth device such as hci0
  --loglevel {info,notice,none,warning,critical,error,debug} Log Level for the daemon
  --port PORT           Server Port
  --daemonname DAEMONNAME Daemon Name
```
