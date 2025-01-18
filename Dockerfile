FROM python:3.11-alpine

COPY requirements.txt /tmp/
RUN python -m pip install --upgrade pip
RUN python -m pip install -r /tmp/requirements.txt

ADD ./flaskapp /opt/app
RUN mkdir /opt/app/logs
RUN touch /opt/app/logs/log.json
WORKDIR /opt/app

EXPOSE 8000

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_APP=app.py
ENV FLASK_RUN_PORT=8000

CMD ["flask","run"]
