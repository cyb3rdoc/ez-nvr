# EZ-NVR - Easy Network Video Recorder

[![Repo](https://img.shields.io/badge/Docker-Repo-007EC6?labelColor-555555&color-007EC6&logo=docker&logoColor=fff&style=flat-square)](https://hub.docker.com/r/cyb3rdoc/eznvr)
[![Version](https://img.shields.io/docker/v/cyb3rdoc/eznvr/latest?labelColor-555555&color-007EC6&style=flat-square)](https://hub.docker.com/r/cyb3rdoc/eznvr)
[![Size](https://img.shields.io/docker/image-size/cyb3rdoc/eznvr/latest?sort=semver&labelColor-555555&color-007EC6&style=flat-square)](https://hub.docker.com/r/cyb3rdoc/eznvr)
[![Pulls](https://img.shields.io/docker/pulls/cyb3rdoc/eznvr?labelColor-555555&color-007EC6&style=flat-square)](https://hub.docker.com/r/cyb3rdoc/eznvr)

This is a simple and easy Network Video Recorder (NVR) that is designed to run on cheap hardware, such as a Raspberry Pi with a hard drive. 24/7 video streams from network cameras are saved. Recorded files can be browsed using [filebrowser](https://github.com/filebrowser/filebrowser).

The project is deliberately bare-bones, configuration is done through `config.yaml` file and deployed using docker containerization.

The camera video streams are saved in 5 minute files (to prevent long periods of video loss should a file become corrupted). At 01:00 UTC, the video files for the previous day are concatenated into a single 24 hour file, and the 5 minute video files are deleted. At 02:00 UTC, the video files older than 21 days are deleted. Period of retention can be changed with `config.yaml` file.

`ffmpeg` is used to connect to the camera streams and save the video feeds. Recording will restart automatically in case of unexpected interruption.

## Configuration Options

1. Use `TZ: Europe/London` environment variable to have filenames in local timezone of London.
2. Set retention period of video files by updating `video_store: 21` to your desired days in `config.yaml` file. (Optional)
3. For password protected RTSP streams, you need pass the argument in RTSP URL configuration based on your camera. E.g., rtsp://user:password@camera-ip/live/stream_01
4. Length of video clip sections can be changed by updating `camera_interval: 300` to desired value. (Optional)
5. Logs can be accessed in native docker logs.

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
Logs can be accessed with `docker logs eznvr`. For detailed logs, use docker environment variable `DEBUG=true` in docker command or docker-compose.yml file.
