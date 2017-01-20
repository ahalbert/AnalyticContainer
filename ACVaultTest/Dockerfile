#@IgnoreInspection BashAddShebang
############################################################
# ACVaultTest
# Dockerfile to build Python Example (One) Analytic Application Containers
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
#
FROM ubuntu:14.04
MAINTAINER Chris Bergh <cbergh@datakitchen.io>

# Add the application resources URL
#RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*
# Update the sources list
RUN apt-get update

# Install basic applications
RUN sudo apt-get install -y tar git curl nano wget dialog net-tools build-essential emacs

# Install Python and Basic Python Tools
RUN sudo apt-get install -y python python-dev python-distribute python-pip


# make a directory for the server
RUN mkdir /dk
RUN mkdir /dk/AnalyticContainer
RUN mkdir /dk/AnalyticContainer/ACVaultTest
RUN mkdir /dk/AnalyticContainer/AnalyticContainerLibrary


#setup that libraries
COPY __init__.py                                /dk/AnalyticContainer/__init__.py
COPY ACVaultTest/__init__.py                   	/dk/AnalyticContainer/ACVaultTest/__init__.py
COPY ACVaultTest/ACVaultTest.py               	/dk/AnalyticContainer/ACVaultTest/ACVaultTest.py
COPY AnalyticContainerLibrary/__init__.py       /dk/AnalyticContainer/AnalyticContainerLibrary/__init__.py
COPY AnalyticContainerLibrary/ACBase.py         /dk/AnalyticContainer/AnalyticContainerLibrary/ACBase.py
COPY AnalyticContainerLibrary/ACSettings.py     /dk/AnalyticContainer/AnalyticContainerLibrary/ACSettings.py
COPY AnalyticContainerLibrary/ACSingletons.py   /dk/AnalyticContainer/AnalyticContainerLibrary/ACSingletons.py

# Set the default directory where CMD will execute
WORKDIR /dk/AnalyticContainer/ACVaultTest

ENV PYTHONPATH=/dk

# Set the default command to execute
CMD python ACVaultTest.py


