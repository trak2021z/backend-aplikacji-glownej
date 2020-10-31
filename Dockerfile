FROM alpine:latest

RUN apk update
RUN apk add --no-cache \
    python3 \
    py3-pip 

ADD ./ /usr/src/app
WORKDIR /usr/src/app/BackendServer

RUN pip3 install -r requirements.txt
RUN curl -OL https://raw.githubusercontent.com/mrako/wait-for/master/wait-for && chmod +x wait-for && chmod +x db-ops.sh
