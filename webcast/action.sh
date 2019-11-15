#!/bin/bash

# Export enviroment vars set in action.conf
# https://unix.stackexchange.com/a/79077
set -a
. ./action.env
set +a

for arg; do

  if [[ $arg == 'build' ]] ; then

    envsubst '$X_DOCKER_IP' < "nginx.conf.example" > "nginx.conf"
    envsubst '$X_DOCKER_IP' < "player.html.example" > "player.html"

    echo "Building docker with network '$X_DOCKER_IP'"
    docker build -t nginx-webcast:latest -f dockerfile .

  elif [[ $arg == 'start' ]]; then

    echo "Starting..."
    export X_CONTAINER_HASH=$(docker run -d -p 80:80 -p 8080:8080 -p 1935:1935 --rm nginx-webcast:latest)
    #export X_CONTAINER_HASH=$(docker ps -lq)
    echo "Docker is running with hash '$X_CONTAINER_HASH'"
    sleep 2
    docker ps

  elif [[ $arg == 'stop' ]]; then

    echo "Stopping $X_CONTAINER_HASH"
    docker stop $X_CONTAINER_HASH

  elif [[ $arg == 'restart' ]]; then

    echo "Stopping $X_CONTAINER_HASH"
    docker stop $X_CONTAINER_HASH
    echo "Starting..."
    export X_CONTAINER_HASH=$(docker run -d -p 80:80 -p 8080:8080 -p 1935:1935 --rm nginx-webcast:latest)
    echo "Docker is running with hash '$X_CONTAINER_HASH'"
    sleep 1
    docker ps

  elif [[ $arg == 'exec' ]]; then

    echo "Entering $X_CONTAINER_HASH"
    docker exec -it $X_CONTAINER_HASH bash

  else
    echo "No good args provided."
  fi
done
