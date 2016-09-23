#!/bin/bash

chmod 777 *.sh

killall nginx
nginx
fuser -k 1234/tcp
uwsgi allsite_web_uwsgi_config.ini

#python allsite_web_main.py &> ./allsite_web_server.log
