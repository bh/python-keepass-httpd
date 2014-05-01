Python Keepass HTTPd
====================
.. image:: https://badge.fury.io/py/keepass_http.png
   :target: http://badge.fury.io/py/keepass_http
.. image:: https://pypip.in/d/keepass_http/badge.png
   :target: https://crate.io/packages/keepass_http/
.. image:: https://travis-ci.org/bh/python-keepass-httpd.png?branch=master
   :target: https://travis-ci.org/bh/python-keepass-httpd
.. image:: https://coveralls.io/repos/bh/python-keepass-httpd/badge.png
   :target: https://coveralls.io/r/bh/python-keepass-httpd

Description
-----------

Installation
------------

on Archlinux
^^^^^^^^^^^^

Use `Yaourt <http://archlinux.fr/yaourt-en/>`_ to install ``python-keepass-httpd``. If it is installed you can install ``python-keepass-httpd`` with:

.. code:: bash

    $ yaourt -S python-keepass-httpd-git

Yaourt will install the package and its dependencies.

Usage
-----

You can see the usage with:

.. code:: bash

    $ python-keepass-httpd --help

The output should be look like this:

::

    Usage:
      python-keepass-httpd run <database_path> [options]
      python-keepass-httpd (-h | --help)
      python-keepass-httpd --version

    Options:
      --help                    Show this screen.
      -v --version              Show version.
      -d --daemon               Start as daemon
      -p --port PORT            Specify a port [default: 19455]
      -h --host HOST            Specify a host [default: 127.0.0.1]
      -l --loglevel LOGLEVEL    Loglevel to use [default: INFO]
      --gui                     Use TKinter for a graphical interface


Starting the server
^^^^^^^^^^^^^^^^^^^

.. code:: bash

    $ python-keepass-httpd run /home/kiwisauce/Dropbox/test.kdb
    2014-03-07 13:28:04,534 [INFO] keepass_http_script: Server started on 127.0.0.1:19455

The server was started. Now we have to setup ChromeIPass.

Setting up `ChromeIPass <https://chrome.google.com/webstore/detail/chromeipass/ompiailgknfdndiefoaoiligalphfdae>`_
------------------------------------------------------------------------------------------------------------------

