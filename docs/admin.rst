***************************
Administrator documentation
***************************

This documentation is for the administration of Opinioxx.

Installation
============

The installation via docker container is strongly recommended.

Requirements
------------

* A working `Docker <https://docs.docker.com/engine/install/>`_ installation
* A SMTP server to send out mails
* A HTTP reverse proxy to enable HTTPS
* A database server (or container)

.. note:: Please do not run Opinioxx without HTTPS encryption - otherwise the login data of your users is transmitted in plaintext and is readable by everyone!

Data folders
------------

First of all, we need to setup the location of the stored data (logfiles) and settings-file:

.. code-block::

   # mkdir /docker/opinioxx
   # mkdir /docker/opinioxx/data
   # chown -R 12421:12421 /docker/opinioxx
   # chmod -R 400 /docker/opinioxx
   # chmod -R 700 /docker/opinioxx/data

.. note:: The user id 12421 is used inside the container and it should be ensured that on the host no user exists with this id

Config file
-----------

Create a config file under `/docker/opinioxx/settings.py` with the content from the `sample-file <https://github.com/opinioxx/opinioxx/blob/master/src/opinioxx/sample_settings.py>`_. Adjust it to your needs.

Database
--------

If you just want to test the tool, you can use the default `db.sqlite3` file as database. Otherwise please choose a database of your choice and add the connection data in the settings file. More information can be found `here <https://docs.djangoproject.com/en/3.1/ref/settings/#databases>`_.

An example for a mysql-database would be the following:

.. code-block::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'mydatabase',
            'USER': 'dbuser',
            'PASSWORD': 'dbpassword',
            'HOST': '127.0.0.1',
            'PORT': '3306',
            'CONN_MAX_AGE': 3600,
        }
    }

Docker
------

Start the docker container:

.. code-block::

   # docker run -p 127.0.0.1:8000:8000 -v /docker/opinioxx/settings.py:/opinioxx/src/opinioxx/settings.py -v /docker/opinioxx/data:/data -d opinioxx/stable:latest

Visit http://127.0.0.1:8000 to see your installation.

.. note:: Your installation is only available on the host system. Configure your HTTP proxy accordingly to make it accessible from the outside.

Cronjob
-------

In order to get the mail notifications working, please add the following to `/etc/crontab`:

.. code-block::

   0  1    * * *   root    wget <YOUR_URL>/cron &> /dev/null

This will generate the mail notifications at 1 am. Please note that the tool only generates notifications for all changes until yesterday - so nothing will happen if you execute the cron script more than once per day.
This is done to prevent inference of the time of actions on persons.