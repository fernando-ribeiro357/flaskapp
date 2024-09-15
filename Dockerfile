FROM python:3.11-alpine

COPY ./requirements.txt /tmp
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt


ADD ./flaskapp /opt/app

WORKDIR /opt/app

EXPOSE 8000

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_APP=./
ENV FLASK_RUN_PORT=8000
ENV FLASK_ENV=development

CMD ["flask","run"]
