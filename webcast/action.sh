#!/bin/bash

ACT=$1

if [[ $ACT == 'build' ]] ; then

  echo "Building..."
  docker build -t stake:latest -f dockerfile .

elif [[ $ACT == 'start' ]]; then

  echo "Starting..."
  export X_IMAGE_HASH=$(docker ps -lq)
  echo "Docker is running with hash '$X_IMAGE_HASH'"

elif [[ $ACT == 'stop' ]]; then

  echo "Stopping $X_IMAGE_HASH"
  docker stop $X_IMAGE_HASH

else

  echo "No good args provided."

fi
