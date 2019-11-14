# nginx-webcast
An attempt to make a webcasting platform and website.

# Webcast setup #

## Local Build and Run ##

### Setup action.conf ###

Environment variables to be used by `action.sh`.

The `X_DOCKER_IP` is the bridge ip of the docker network, e.g. `172.17.0.1`.
This can be found by `ip a | grep docker0 | grep init`.
We could use `--network=host` on `docker run` but I rather have a locked down network from the start.
https://docs.docker.com/v17.09/engine/userguide/networking/#default-networks  

### Docker container actions ###

```
cd ./webcast

# Build docker image
source ./action.sh build

# Start docker container running nginx  
source ./action.sh start

# Stop docker container running nginx
source ./action.sh stop

# Restart docker nginx container
source ./action.sh restart
```

### Broadcast stream ###

While not the only way, I'm using OBS (Open Broadcast Software, https://obsproject.com/) to transmit an image to `rtmp://$X_DOCKER_IP/stream/`.

### Watch stream via RTMP ###

While not the only way, I'm using VLC to receive `rtmp://$X_DOCKER_IP/stream/<key>`.

### Watch stream via webpage ###

Go to `http://$X_DOCKER_IP:8080/`.

### Download stream recordings ###

Go to `http://$X_DOCKER_IP:8080/recordings/`
