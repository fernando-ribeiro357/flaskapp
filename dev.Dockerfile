FROM python:3.11-alpine

COPY ./requirements-dev.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt


ADD ./flaskapp /opt/app

# Criação do diretório de logs
RUN [ -d /opt/app/logs ] || mkdir /opt/app/logs 

WORKDIR /opt/app

EXPOSE 8000

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_APP=./
ENV FLASK_RUN_PORT=8000
ENV FLASK_ENV=development

CMD ["flask","run","--debug"]
