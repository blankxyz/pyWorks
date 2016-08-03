#!/bin/bash

ps -ef | grep allsite_list | grep -v grep | awk '{print $2}'| xargs kill -9

