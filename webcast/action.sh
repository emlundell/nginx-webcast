#!/bin/bash

ACT=$1

# Export enviroment vars set in action.conf
# https://unix.stackexchange.com/a/79077
set -a
. ./action.conf
set +a

if [[ $ACT == 'build' ]] ; then

  envsubst '$X_DOCKER_IP' < "nginx.conf.example" > "nginx.conf"
  envsubst '$X_DOCKER_IP' < "dash.html.example" > "dash.html"

  echo "Building docker with network '$X_DOCKER_IP'"
  docker build -t nginx-webcast:latest -f dockerfile .

elif [[ $ACT == 'start' ]]; then

  echo "Starting..."
  export X_IMAGE_HASH=$(docker run -d -p 8080:8080 -p 1935:1935 --rm nginx-webcast:latest)
  #export X_IMAGE_HASH=$(docker ps -lq)
  echo "Docker is running with hash '$X_IMAGE_HASH'"

elif [[ $ACT == 'stop' ]]; then

  echo "Stopping $X_IMAGE_HASH"
  docker stop $X_IMAGE_HASH

elif [[ $ACT == 'restart' ]]; then

  echo "Stopping $X_IMAGE_HASH"
  docker stop $X_IMAGE_HASH
  echo "Starting..."
  export X_IMAGE_HASH=$(docker run -d -p 8080:8080 -p 1935:1935 --rm nginx-webcast:latest)
  #export X_IMAGE_HASH=$(docker ps -lq)
  echo "Docker is running with hash '$X_IMAGE_HASH'"

else

  echo "No good args provided."

fi
