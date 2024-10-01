FROM python:3.11-slim


ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y gcc musl-dev linux-headers-amd64 make libexpat1-dev
    
COPY ./requirements.txt /tmp
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

RUN pip install mod_wsgi-standalone

#  Copiando aplicação
ADD ./flaskapp /opt/app

# Criação do diretório de logs
RUN [ -d /opt/app/logs ] || mkdir /opt/app/logs

RUN echo "" >> /opt/app/logs/log.json && \
    adduser -S -D -H -G www-data www-data && \
    chown -R www-data:www-data /opt/app/logs/

WORKDIR /opt/app

EXPOSE 8000

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_APP=./
ENV FLASK_RUN_PORT=8000
# ENV FLASK_ENV=development

CMD mod_wsgi-express start-server --processes 4 \
                                  --user www-data --group www-data \
                                  --host 0.0.0.0 \
                                  --entry-point wsgi.py
