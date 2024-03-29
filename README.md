# EZ-NVR - Easy Network Video Recorder

[![Repo](https://img.shields.io/badge/Docker-Repo-007EC6?labelColor-555555&color-007EC6&logo=docker&logoColor=fff&style=flat-square)](https://hub.docker.com/r/cyb3rdoc/eznvr)
[![Version](https://img.shields.io/docker/v/cyb3rdoc/eznvr/latest?labelColor-555555&color-007EC6&style=flat-square)](https://hub.docker.com/r/cyb3rdoc/eznvr)
[![Size](https://img.shields.io/docker/image-size/cyb3rdoc/eznvr/latest?sort=semver&labelColor-555555&color-007EC6&style=flat-square)](https://hub.docker.com/r/cyb3rdoc/eznvr)
[![Pulls](https://img.shields.io/docker/pulls/cyb3rdoc/eznvr?labelColor-555555&color-007EC6&style=flat-square)](https://hub.docker.com/r/cyb3rdoc/eznvr)

This is a simple and easy Network Video Recorder (NVR) that is designed to run on cheap hardware, such as a Raspberry Pi with a hard drive. 24/7 video streams from network cameras are saved. Recorded files can be browsed using [filebrowser](https://github.com/filebrowser/filebrowser).

The project is deliberately bare-bones, configuration is done through `config.yaml` file and deployed using docker containerization.

The camera video streams are saved in 5 minute files (to prevent long periods of video loss should a file become corrupted). At 01:00 UTC, the video files for the previous day are concatenated into a single 24 hour file, and the 5 minute video files are deleted. At 02:00 UTC, the video files older than 21 days are deleted. Period of retention can be changed with `config.yaml` file.

`ffmpeg` is used to connect to the camera streams and save the video feeds. Recording will restart automatically in case of unexpected interruption.

## Build image using Dockerfile

Clone the repo to build your own image.

```
TIMESTAMP="$(date '+%Y%m%d-%H%M')"

docker build -t "${USER?}/eznvr:${TIMESTAMP}" .
```

Run eznvr docker container:
```
docker run -d --name eznvr -v /path/to/eznvr/config:/config -v /path/to/eznvr/storage:/storage your_username/eznvr:YYYYMMDD-HHMM
```

Mount following volumes to update camera settings and access or backup stored video files.
1. /config - For NVR configuration
2. /storage - For recorded videos

## Using docker-compose.yml

You can also use prebuilt image cyb3rdoc/eznvr:latest (`dev` tag for developmental image) with docker-compose.yml.
```
version: '3.6'
services:
  eznvr:
    container_name: eznvr
    hostname: eznvr
    image: cyb3rdoc/eznvr:latest
    volumes:
      - /path/to/eznvr/config:/config
      - /path/to/eznvr/storage:/storage
    restart: unless-stopped

```

## NVR Logs
Logs are saved in /var/log/nvr.log file. This can be accessed with `docker exec -it eznvr cat /var/log/nvr.log` OR viewed live with `docker exec -it eznvr tail -F /var/log/nvr.log`
