FROM alpine:latest

RUN apk update
RUN apk add --no-cache \
    git \
    python3 \
    py3-pip 

WORKDIR /
RUN git clone https://github.com/aplikacje-internetowe-l2/backend-aplikacji-glownej.git 

WORKDIR /backend-aplikacji-glownej/BackendServer
RUN pip3 install -r requirements.txt
RUN python3 manage.py migrate --noinput
