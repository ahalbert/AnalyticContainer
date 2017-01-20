#@IgnoreInspection BashAddShebang
############################################################
# PostgresContainer
# Dockerfile to build Python Example (One) Analytic Application Containers
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
#
FROM ubuntu:14.04
MAINTAINER Chris Bergh <cbergh@datakitchen.io>

# Update the sources list
RUN sudo apt-get update

# Add the application resources URL
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list


# Install basic applications
RUN sudo apt-get install -y tar git curl nano wget dialog net-tools build-essential emacs

# Install Python and Basic Python Tools
RUN sudo apt-get install -y python libpq-dev python-dev python-distribute python-pip


# make a directory for the server
RUN mkdir /dk
RUN mkdir /dk/AnalyticContainer
RUN mkdir /dk/AnalyticContainer/PostgresContainer
RUN mkdir /dk/AnalyticContainer/AnalyticContainerLibrary


#setup that libraries
COPY __init__.py                                /dk/AnalyticContainer/__init__.py
COPY PostgresContainer/__init__.py             /dk/AnalyticContainer/PostgresContainer/__init__.py
COPY PostgresContainer/PostgresContainer.py   /dk/AnalyticContainer/PostgresContainer/PostgresContainer.py
COPY PostgresContainer/requirements.txt        /dk/AnalyticContainer/PostgresContainer/requirements.txt
COPY AnalyticContainerLibrary/__init__.py       /dk/AnalyticContainer/AnalyticContainerLibrary/__init__.py
COPY AnalyticContainerLibrary/ACBase.py         /dk/AnalyticContainer/AnalyticContainerLibrary/ACBase.py
COPY AnalyticContainerLibrary/ACSettings.py     /dk/AnalyticContainer/AnalyticContainerLibrary/ACSettings.py
COPY AnalyticContainerLibrary/ACSingletons.py   /dk/AnalyticContainer/AnalyticContainerLibrary/ACSingletons.py
COPY AnalyticContainerLibrary/ACPostgresSQL.py  /dk/AnalyticContainer/AnalyticContainerLibrary/ACPostgresSQL.py
COPY AnalyticContainerLibrary/ACEmail.py        /dk/AnalyticContainer/AnalyticContainerLibrary/ACEmail.py

# Set the default directory where CMD will execute
WORKDIR /dk/AnalyticContainer/PostgresContainer


# Install Python requirements
RUN sudo pip install -r requirements.txt

ENV PYTHONPATH=/dk

# Set the default command to execute
CMD python PostgresContainer.py


