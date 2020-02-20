#!/bin/bash
set -e

sshfs -o nonempty,allow_other stream@web:/home/stream/media /home/stream/media/
#sshfs -o nonempty,allow_other stream@web:/var/log/nginx/ /var/log/nginx/
nginx

/bin/bash
