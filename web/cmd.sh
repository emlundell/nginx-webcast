#!/bin/bash
set -e 

service syslog-ng start
service ssh start
nginx

/bin/bash
