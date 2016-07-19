#!/usr/bin/env bash
ps -ef | grep allsite_url_rule_manual | grep -v grep | awk '{print $2}' |xargs kill -9
