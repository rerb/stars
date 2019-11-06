# pull official base image
FROM python:2.7.16-stretch

# RUN apt-cache search mysql-server

RUN apt-get update \
    && apt-get -y install \
    default-libmysqlclient-dev \
    build-essential \
    python-dev \
    mysql-common \
    python-mysqldb \
    rabbitmq-server

# set work directory
WORKDIR /usr/src/app

# install dependencies
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/
