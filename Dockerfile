FROM ubuntu:22.04
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y curl vim nodejs npm python3 pip

COPY ./ai /opt/ai
COPY ./decision_tree /opt/decision_tree
COPY ./frontend /opt/frontend
COPY ./plo_project /opt/plo_project
COPY ./poker /opt/poker
COPY ./venv /opt/venv
COPY ./*.* /opt/

WORKDIR /opt/
RUN pip install -r /opt/requirements.txt
RUN python3 manage.py migrate

WORKDIR /opt
RUN npm install
WORKDIR /opt/frontend
RUN npm install
RUN npm run build

RUN rm -rf /opt/poker/templates/build
RUN rm -rf /opt/poker/static/static
RUN mv /opt/frontend/build /opt/poker/templates/
RUN mv /opt/poker/templates/build/static /opt/poker/static

EXPOSE 8000
EXPOSE 80
EXPOSE 443

WORKDIR /opt
CMD ./start.sh
