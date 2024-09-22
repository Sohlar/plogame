FROM nvidia/cuda:12.1.1-base-ubuntu22.04

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y curl vim python3 pip

WORKDIR /app

RUN mkdir logs models

ARG REQUIREMENTS=requirements_cpu.txt
COPY ./$REQUIREMENTS /app/requirements.txt

RUN pip install -r requirements.txt
