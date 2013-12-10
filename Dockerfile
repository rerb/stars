FROM ubuntu

MAINTAINER Bob Erb <bob.erb@gmail.com>

# Update and upgrade package repo:
RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install mysql-server libmysqlclient-dev -y
RUN apt-get install sqlite3 libsqlite3-dev -y
RUN apt-get install mercurial -y
# Prerequisites for pip:
RUN apt-get install python-setuptools python-dev build-essential -y

# Install pip.
RUN easy_install pip 

# Install virtualenv.
RUN pip install virtualenv 
# RUN pip install virtualenvwrapper

# # Config ssh
# RUN apt-get install ssh -y
# # Fix /etc/ssh/ssh_config (http://goo.gl/bvJxrj):
# RUN echo " IdentityFile ~/.ssh/id_rsa" >> /etc/ssh/ssh_config

# # Copy a bitbucket key over:
# # ADD ~/.ssh/id_rsa.pub /root/.ssh/
# # ADD ~/.ssh/id_rsa /root/.ssh/
# # ADD ~/.ssh/config /root/.ssh/config
# # RUN chown root:root /root/.ssh/*

# # Check out the STARS source.
# # RUN hg clone -yv ssh://hg@bitbucket.org/aashe/stars /var/local --ssh "ssh -o StrictHostKeyChecking=no"

# # Assumining $CWD is a STARS checkout:
# RUN mkdir /var/local/stars
ADD . /opt/apps/stars

# Set up environment for mkvirtualenv.
# ENV WORKON_HOME /var/local/stars

# Set up a virtualenv for STARS.
# RUN bash -c "source /usr/local/bin/virtualenvwrapper.sh && mkvirtualenv stars --no-site-packages; exit 0"
RUN virtualenv --no-site-packages /opt/virtualenvs/stars

# pip install requirements.txt.
# RUN bash -c "source /usr/local/bin/virtualenvwrapper.sh && workon stars && cd $WORKON_HOME && pip install -r requirements.txt; exit 0"
RUN /opt/virtualenvs/stars/bin/pip install -r /opt/apps/stars/requirements_dev.txt
RUN /opt/virtualenvs/stars/bin/pip install -r /opt/apps/stars/requirements.txt

EXPOSE 8000

