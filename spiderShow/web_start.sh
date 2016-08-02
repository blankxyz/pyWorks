#!/bin/bash
chmod 777 *.sh
source ../../venv/bin/activate
python allsite_web_run.py &> ./web_server.log


