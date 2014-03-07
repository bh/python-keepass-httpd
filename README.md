# Python Keepass HTTPd #
[![Coverage Status](https://coveralls.io/repos/bhedrich/python-keepass-httpd/badge.png)](https://coveralls.io/r/bhedrich/python-keepass-httpd)
[![Build Status](https://travis-ci.org/bhedrich/python-keepass-httpd.png?branch=master)](https://travis-ci.org/bhedrich/python-keepass-httpd)

## Description ##

## Installation ##

#### on Archlinux ####
Use [Yaourt](http://archlinux.fr/yaourt-en/) to install ```python-keepass-httpd``` 
If it is installed you can install ```python-keepass-httpd``` with:
```bash
$ yaourt -S python-keepass-httpd-git
```
Yaourt will install the package and its dependencies. 

## Usage ##
You can see the usage with:
```bash
$ python-keepass-httpd --help
```

The output should be look like this:
```
Usage:
  ./python-keepass-httpd.py start <database_path> <passphrase> [options]
  ./python-keepass-httpd.py (-h | --help)
  ./python-keepass-httpd.py --version

Options:
  --help                    Show this screen.
  -v --version              Show version.
  -d --daemon               Start as daemon
  -p --port PORT            Specify a port [default: 19455]
  -h --host HOST            Specify a host [default: 127.0.0.1]
  -l --loglevel LOGLEVEL    Loglevel to use [default: INFO]
```
### Starting the server ###
```
$ python-keepass-httpd start /home/kiwisauce/Dropbox/test.kdb my_secure_password
2014-03-07 13:28:04,534 [INFO] keepass_http_script: Server started on 127.0.0.1:19455
```
The server was started. Now we have to setup ChromeIPass.

### Setting up [ChromeIPass](https://chrome.google.com/webstore/detail/chromeipass/ompiailgknfdndiefoaoiligalphfdae) ###

