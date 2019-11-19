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

# install dependencies
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

COPY ./requirements.txt /usr/src/app/requirements.txt
WORKDIR /usr/src/app
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/

# # Collect Static
# WORKDIR /usr/src/app
# RUN python manage.py collectstatic --noinput

# # Run migrations
# WORKDIR /usr/src/app
# RUN python manage.py migrate

