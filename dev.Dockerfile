FROM python:3.11

COPY ./requirements.txt /tmp
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

RUN mkdir /opt/app

## Em vez de copiar a aplicação, criar volume bind
## ./flaskapp:/opt/app
# COPY ./flaskapp /opt/app

WORKDIR /opt/app

EXPOSE 8000

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_APP=./
ENV FLASK_RUN_PORT=8000
ENV FLASK_ENV=development

CMD ["flask","run"]
