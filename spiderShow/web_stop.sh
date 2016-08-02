#!/bin/bash
ps -ef | grep allsite_ | grep -v grep | awk '{print $2}'|xargs kill -9
