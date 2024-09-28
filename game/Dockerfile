FROM pybase as builder

EXPOSE 80
EXPOSE 443

COPY ./Backend/* /app/

WORKDIR /app

RUN mkdir -p models logs