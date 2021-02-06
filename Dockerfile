FROM debian as builder
LABEL maintainer="Frederic Aoustin <fraoustin@gmail.com>"

RUN apt-get update && apt-get install -y \
        minify \
    && rm -rf /var/lib/apt/lists/* 

RUN mkdir /costu
RUN mkdir /costu/files
COPY ./files/ /costu/files/
WORKDIR /costu/files/css
RUN minify -o icon.css icon.css
RUN minify -o costu.css costu.css
WORKDIR /costu/files/javascripts
RUN minify -o costu.js costu.js

FROM python:3.8-alpine

RUN mkdir /data
VOLUME /data

RUN mkdir /img
VOLUME /img

RUN mkdir /costu
COPY . /costu/
RUN rm -rf /costu/files
COPY --from=builder /costu/files /costu/files
RUN rm -rf /costu/entrypoint.sh

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN pip install -r /costu/REQUIREMENTS.txt

ENV COSTU_PORT 5000
ENV COSTU_DEBUG false
ENV COSTU_HOST 0.0.0.0
ENV COSTU_DIR /data
ENV COSTU_IMG /img

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["costu"]