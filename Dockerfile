FROM python:3.11
# FROM python:3.11-slim

COPY ./requirements.txt /tmp
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y gcc musl-dev linux-headers-amd64 make libexpat1-dev
    
RUN pip install mod_wsgi-standalone

RUN mkdir /opt/app

#  Copiando aplicação
COPY ./flaskapp /opt/app

RUN adduser -S -D -H -G www-data www-data

RUN chown -R www-data:www-data /opt/app/logs/

WORKDIR /opt/app


EXPOSE 8000

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_APP=./
ENV FLASK_RUN_PORT=8000
ENV FLASK_ENV=development

CMD mod_wsgi-express start-server --processes 4 \
                                  --user www-data --group www-data \
                                  --host 0.0.0.0 \
                                  --entry-point wsgi.py
