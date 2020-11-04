FROM alpine:latest

RUN apk update
RUN apk add --no-cache \
    python3 \
    py3-pip \
    postgresql-dev \
    gcc \
    musl-dev \
    python3-dev \
    curl

ADD ./ /usr/src/app
WORKDIR /usr/src/app/BackendServer

RUN pip3 install -r requirements.txt
RUN curl -OL https://raw.githubusercontent.com/mrako/wait-for/master/wait-for && chmod +x wait-for && chmod +x db-ops.sh
RUN python3 manage.py migrate --noinput
RUN pip3 install -r requirements.txt
RUN python3 manage.py migrate
RUN python3 manage.py loaddata companies
RUN python3 manage.py shell < seed_stocks.py
RUN python3 manage.py createsuperuser
