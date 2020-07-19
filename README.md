# Nginx Webcast
An attempt to make a webcasting platform and website.

_**This project is a work in progress. I am learning as I go (don't we all?) This is not currently ready for production.**_

## Introduction

The main impetus for this project is that my church has need of a better webcasting service. Many of the current online services are deficit in one or more areas.

The following requirements are greatly desired:

- **Low cost**. Many online services cost $60+/mo for a hot server. But we are not broadcasting that often and so are paying for lots of dead server time. It would be prefered that we only pay for what we need.

- **Live streaming of medium and small events**. Most of the time there are only expected to be six viewers for small events and a couple hundred for the largest events. The small events happen once or twice a week. The larger events only every few month. 

- **Content security**. It is expected that most people will only get the live streaming. However, some people will need recordings and thus recordings are a smaller priority. Even then, these recordings are not to be passed around to everyone.

- **Low internet speeds**. Many viewers have lousy internet bandwidth. Some can only stream audio. The bitrates have to support the spectrum of user needs. Many online service providers cannot support speeds that are required.

- **Users per stream**. It's nice to know how many people are watching the particular stream. This problem is not as easy to solve. 

Looking around the internet for possible solutions, there are many examples of making pieces of a webcasting platform. However, there are very few complete, free solutions that are easily managed let alone satisfy the above requirements.

Some market research suggests that I might be able to create a working solution that works at the desired costs. This project is an attempt to create that solution using coding experience and skills that I have gained at my employment and elsewhere. 

## The Status of Things

- Using docker-compose, three containers are spun up:
    1. The webserver and log handler
    2. The rtmp server for processing incoming rtmp streams
    3. Haproxy load balancer to interface with the outside world
    4. One network to connect them all

- Within the rtmp server, the incoming rtmp stream is encoded to different bitrates via ffmpeg.

- When a stream has stopped, the stream is transcoded as both mp3 and mp4 and then ssh'ed. With an eye towards multiple concurrent streams, a more distributive pattern was taken with all logs and files being sent to the webserver.
    1. Logs are handled by syslog-ng.
    2. mp3 and mp4 files are sent via a sshfs mount. There was no guarantee that future platforms would have a shareable nfs mount.

- `video.js` is used to view the stream on the webpage.

- There is no admin page or authentication/authorization.
- There is no storage mount for the logs and webserver. Once the container is stopped, they are gone.
- Attempts to get the connections per stream have been made but are not complete. A `parse_db.py` script was created to help with this.
- Stats of the various processes are found on port 8080. You can never get enough stats and logs.

## Local Build and Run ##

### Docker container actions ###

To make development easier, a basic bash wrapper was created to handle the details of stopping, building, and starting the containers. 

```
# Build docker-compose
./action.sh build

# Start docker-compose
./action.sh start

# Stop docker-compose
./action.sh stop

# Do everything in sequence
./action.sh stop build start

# Get docker-compose logs
./action.sh logs
```

Building the image could leave dangling docker images. It would be wise to occasionally run `docker image prune`. 

### Setup action.env ###

Environment variables to be used by `action.sh`.

```
X_DOCKER_IP=127.0.0.1
NGINX_VERSION=nginx-1.15.0
NGINX_RTMP_MODULE_VERSION=1.2.1
```

_While `localhost` works, this requires the network to be somewhat open. In the future, things will be more locked down._

`X_DOCKER_IP` is the bridge ip of the docker network, e.g. `172.17.0.1`.
This can be found by `ip a | grep docker0 | grep init`.
We could use `--network=host` on `docker run` but I rather have a locked down network from the start.
https://docs.docker.com/v17.09/engine/userguide/networking/#default-networks

`NGINX_VERSION` and `NGINX_RTMP_MODULE_VERSION` are used in building the custom nginx rtmp module.

### Broadcast stream ###

While not the only possible way, I'm using OBS (Open Broadcast Software, https://obsproject.com/) to transmit an image to `rtmp://localhost/stream/`. I usually use the Bucky the Bunny video set.  Set the `key` to something useful like `test`. The port will automatically be 1935.

### Watch stream via webpage ###

Go to `http://localhost`

The webpage has two objects recieving a HLS video (by default) and HLS audio. 

The bitrates possible are 

| Video | Audio |
|-------|-------|
| 128K  | 32K |
| 256k  | 64K |
| 512K  | 128K |
| audio-only | 16K |

The bitrates can be made lower or higher up to the hardware and ffmpeg limitations. These values have been chosen due to known slow internet bandwidths in the target audience.

### Download stream recordings ###

Recordings are created automatically after streaming is stopped. There are no real time transcodings. Video and audio files will be timestamped to when the recording started - not finshed. If a stream is interupted, the streams will be considered seperate files. 

Future development might join similar files within a certain time period.

`mp4` recordings are found on one page at `http://localhost/video/`
`mp3` recordings are found on one page at `http://localhost/audio/`

## Stats

Various stats (useful or otherwise) can be found at 

`http://localhost:8080/web-stats`
`http://localhost:8080/rtmp-stats`
`http://localhost:8080/haproxy`

## Future Work

1. Build out a much more feature rich website
    - Friendly home page to view
    - Admin to handle creating, starting, and showing streams
    - Expected to be written with Vue and Django

2. Deploy to Digital Ocean
    - Expected deployment in k8s for easy management. (Converting from docker-compose to seperate droplets seems too complicated. But I could be wrong about this.)
    - Cheaper and less messy than AWS
    - Might include some CI/CD.
