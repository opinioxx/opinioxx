#!/usr/bin/env bash

export DATA_DIR=/data/

if [ ! -d /data/logs ]; then
    mkdir /data/logs;
fi

cd /opinioxx/src || exit 1
./manage.py collectstatic --clear --noinput
./manage.py migrate

if [ "$1" == "load_demo_data" ]
  then
    ./manage.py loaddata 'demo_data.json'
fi

daphne -b 0.0.0.0 -p 8000 opinioxx.asgi:application