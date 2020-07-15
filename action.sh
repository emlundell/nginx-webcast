#!/bin/bash

#####
# 
# $ ./action.sh build
# $ ./action.sh stop
# $ ./action.sh start
# $ ./action.sh stop build start
#
#####

# Export enviroment vars set in action.conf
# https://unix.stackexchange.com/a/79077
set -ae
. ./action.env
set +a

for arg; do

  if [[ $arg == 'build' ]] ; then

    echo "Building docker with network '$X_DOCKER_IP'"

    # Create a public/private key pair for the sshfs
    ssh-keygen -q -N "" -f id_rsa
    cp id_rsa.pub ./web/
    mv id_rsa* ./rtmp/

    envsubst '$X_DOCKER_IP' < ./web/player.html.example > ./web/player.html

    # *************************************
    # Nginx and RTMP for Ubuntu 20.04 with stub_status_module enabled
    cd ./rtmp_nginx_20_04/

    # Download the rtmp module repo if not exist
    if [ ! -d nginx-rtmp-module ]; then 
        git clone https://github.com/arut/nginx-rtmp-module.git
    fi

    # Download Nginx zip
    if [ ! -f nginx.tar.gz ]; then 
        wget -O nginx.tar.gz https://nginx.org/download/nginx-1.19.0.tar.gz
    fi

    cd ..

    # ******************************************
    # docker-compose doesn't cache image layers. So build the images outside
    docker build -f ./rtmp_nginx_20_04/dockerfile -t rtmp-nginx-20.04:latest ./rtmp_nginx_20_04
    docker build -f ./rtmp/dockerfile -t webcast-rtmp:latest ./rtmp/
    docker build -f ./web/dockerfile -t webcast-web:latest ./web/
    docker build -f ./haproxy/dockerfile -t webcast-haproxy:latest ./haproxy/

  elif [[ $arg == 'start' ]]; then

    echo "Starting..."
    docker-compose up -d
    sleep 2
    docker ps

  elif [[ $arg == 'stop' ]]; then

    echo "Stopping"
    docker-compose down -v

  elif [[ $arg == 'restart' ]]; then

    echo "Restarting"
    docker-compose restart
    sleep 1
    docker ps

  elif [[ $arg == 'logs' ]]; then

    echo "Getting logs"
    docker-compose logs

  else
    echo "No good args provided."
  fi
done
