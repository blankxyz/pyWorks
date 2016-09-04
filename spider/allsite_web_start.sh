#!/bin/bash

chmod 777 *.sh
python allsite_web_main.py &> ./allsite_web_server.log
