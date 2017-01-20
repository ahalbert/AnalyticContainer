#@IgnoreInspection BashAddShebang
############################################################
# TableauContainer
# Based on Ubuntu
############################################################

#FROM selenium/node-chrome:3.0.1-aluminum
#COPY TableauContainer/entry_point.sh /opt/bin/entry_point.sh
#RUN sudo chmod +x /opt/bin/entry_point.sh


##
#EXPOSE 4444
# Set the base image to Ubuntu
#
# Set the base image to Ubuntu
#
FROM ubuntu:14.04
MAINTAINER Chris Bergh <cbergh@datakitchen.io>

# Add the application resources URL
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

RUN sudo apt-get update

RUN sudo apt-get install -y wget

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
RUN sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Update the sources list
RUN sudo apt-get update

# Install basic applications
RUN sudo apt-get install -y tar git curl nano wget dialog net-tools build-essential emacs

RUN sudo apt-get update --fix-missing

# Install Python and Basic Python Tools PLUS XML
RUN sudo apt-get install -y python libpq-dev libxml2-dev libxslt-dev python-dev python-distribute python-pip

RUN curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -

RUN sudo apt-get install -y nodejs

RUN sudo apt-get install -y xvfb google-chrome-stable imagemagick

RUN sudo pip install -U selenium
RUN sudo npm install -g webdriver-manager

RUN sudo webdriver-manager update --chrome

RUN sudo apt-get install -y openjdk-7-jre-headless

# make a directory for the server
RUN  mkdir /dk
RUN  mkdir /dk/AnalyticContainer
RUN  mkdir /dk/AnalyticContainer/TableauContainer
RUN  mkdir /dk/AnalyticContainer/AnalyticContainerLibrary

#setup that libraries
COPY __init__.py                                /dk/AnalyticContainer/__init__.py
COPY TableauContainer/__init__.py               /dk/AnalyticContainer/TableauContainer/__init__.py
COPY TableauContainer/TableauContainer.py       /dk/AnalyticContainer/TableauContainer/TableauContainer.py
COPY TableauContainer/requirements.txt          /dk/AnalyticContainer/TableauContainer/requirements.txt
COPY AnalyticContainerLibrary/__init__.py       /dk/AnalyticContainer/AnalyticContainerLibrary/__init__.py
COPY AnalyticContainerLibrary/ACBase.py         /dk/AnalyticContainer/AnalyticContainerLibrary/ACBase.py
COPY AnalyticContainerLibrary/ACSettings.py     /dk/AnalyticContainer/AnalyticContainerLibrary/ACSettings.py
COPY AnalyticContainerLibrary/ACSingletons.py   /dk/AnalyticContainer/AnalyticContainerLibrary/ACSingletons.py
COPY AnalyticContainerLibrary/ACTableau.py      /dk/AnalyticContainer/AnalyticContainerLibrary/ACTableau.py
COPY TableauContainer/run-selenium.sh 			/dk/AnalyticContainer/TableauContainer/run-selenium.sh 
# Set the default directory where CMD will execute
WORKDIR /dk/AnalyticContainer/TableauContainer


# Install Python requirements
RUN sudo pip install -r requirements.txt

#============================
# Some configuration options
#============================
ENV SCREEN_WIDTH 1360
ENV SCREEN_HEIGHT 1020
ENV SCREEN_DEPTH 24
ENV DISPLAY :99.0
#RUN Xvfb $DISPLAY &
#RUN webdriver-manager start --detach --logging selenium.log
##USER seluser
#CMD ls -l /opt/bin
#CMD cat /opt/bin/entry_point.sh
#CMD ["sudo -u seluser /opt/bin/entry_point.sh"]
#RUN sleep 10
#RUN ps -aux | grep java

# Set the default command to execute
CMD bash run-selenium.sh "python TableauContainer.py"


