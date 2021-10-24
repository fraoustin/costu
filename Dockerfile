FROM debian as builder
LABEL maintainer="Frederic Aoustin <fraoustin@gmail.com>"

RUN apt-get update && apt-get install -y \
        minify \
    && rm -rf /var/lib/apt/lists/* 

RUN mkdir /DESKTOP
RUN mkdir /DESKTOP/files
COPY ./files/ /DESKTOP/files/
WORKDIR /DESKTOP/files/css
RUN minify -o icon.css icon.css
RUN minify -o DESKTOP.css DESKTOP.css
WORKDIR /DESKTOP/files/javascripts
RUN minify -o DESKTOP.js DESKTOP.js

FROM python:3.8-alpine

RUN mkdir /data
VOLUME /data

RUN mkdir /img
VOLUME /img

RUN mkdir /gbi
COPY . /gbi/
RUN rm -rf /gbi/entrypoint.sh

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN pip install -r /gbi/REQUIREMENTS.txt

ENV DESKTOP_PORT 5000
ENV DESKTOP_DEBUG false
ENV DESKTOP_HOST 0.0.0.0
ENV DESKTOP_DIR /data
ENV DESKTOP_IMG /img

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gbi"]