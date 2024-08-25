FROM ubuntu:22.04
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y curl vim nodejs npm python3 pip

COPY ./ai /opt/ai
COPY ./*.* /opt/

WORKDIR /opt/

EXPOSE 80
EXPOSE 443

WORKDIR /opt
CMD ./start.sh
