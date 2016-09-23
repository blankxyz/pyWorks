#!/bin/bash

killall nginx
fuser -k 1234/tcp
#ps -ef| grep allsite_ | grep -v grep | awk '{print $2}'| xargs kill -9


