FROM python:3.11-alpine

COPY ./requirements-dev.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt

ADD ./flaskapp /opt/app

WORKDIR /opt/app

EXPOSE 8000

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_APP=./
ENV FLASK_RUN_PORT=8000

CMD ["flask","run"]
