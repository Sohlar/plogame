FROM ubuntu:22.04
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y curl vim python3 pip

COPY ./requirements.txt /app/
WORKDIR /app

RUN mkdir logs
RUN mkdir models

RUN pip install -r requirements.txt
