#!/usr/bin/env bash
#!/bin/bash
chmod 777 *.sh
source /Users/song/workspace/venv/bin/activate
python allsite_web_run.py &> ./web_server.log


