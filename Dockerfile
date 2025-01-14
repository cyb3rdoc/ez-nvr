FROM python:alpine

LABEL author="cyb3rdoc" maintainer="cyb3rdoc@proton.me"

RUN apk update \
  && apk add --no-cache \
	ffmpeg \
  && rm -rf /var/cache/apk/*

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /

RUN cat /crontab >> /etc/crontabs/root && rm /crontab

VOLUME ["/config", "/storage"]

CMD crond && python /app/nvr.py

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD python /app/healthcheck.py
