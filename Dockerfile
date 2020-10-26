FROM alpine:latest

RUN apk update
RUN apk add --no-cache \
    git \
    python3 \
    py3-pip 

ADD ./ /usr/src/app
WORKDIR /usr/src/app/BackendServer

RUN pip3 install -r requirements.txt
RUN python3 manage.py migrate --noinput
EXPOSE 8000