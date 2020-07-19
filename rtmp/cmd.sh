#!/bin/bash
set -e

service syslog-ng start
sshfs -o nonempty,allow_other stream@web:/home/stream/media /home/stream/media/
nginx

/bin/bash
