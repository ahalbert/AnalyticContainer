#@IgnoreInspection BashAddShebang
############################################################
# PentahoDIContainer
# Based on Ubuntu
############################################################

FROM ubuntu:14.04
MAINTAINER Chris Bergh <cbergh@datakitchen.io>

# Add the application resources URL
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

RUN sudo apt-get update

# Install basic applications
RUN sudo apt-get install -y tar git curl nano wget dialog net-tools build-essential software-properties-common zip

RUN sudo apt-get update --fix-missing

# Install Python and Basic Python Tools PLUS XML
RUN sudo apt-get install -y python libpq-dev libxml2-dev libxslt-dev python-dev python-distribute python-pip

RUN sudo apt-get update

############################################################
# install Oracle Java 1.7
RUN \
  echo oracle-java7-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
  add-apt-repository -y ppa:webupd8team/java && \
  apt-get update && \
  apt-get install -y oracle-java7-installer && \
  rm -rf /var/lib/apt/lists/* && \
  rm -rf /var/cache/oracle-jdk7-installer
# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-7-oracle

############################################################
# Pentaho DI
ENV PDI_RELEASE=5.3 \
    PDI_VERSION=5.3.0.0-213 \
    PDI_HOME=/opt/pentaho-di

RUN curl -L -o /tmp/pdi-ce-${PDI_VERSION}.zip http://downloads.sourceforge.net/project/pentaho/Data%20Integration/${PDI_RELEASE}/pdi-ce-${PDI_VERSION}.zip
RUN unzip -q /tmp/pdi-ce-${PDI_VERSION}.zip -d $PDI_HOME
RUN rm /tmp/pdi-ce-${PDI_VERSION}.zip

ENV PATH=$PDI_HOME/data-integration:$PATH
RUN chmod +x $PDI_HOME/data-integration/pan.sh
RUN chmod +x $PDI_HOME/data-integration/kitchen.sh

############################################################
# AC Container
# make a directory for the server
RUN  mkdir /dk
RUN  mkdir /dk/AnalyticContainer
RUN  mkdir /dk/AnalyticContainer/PentahoDIContainer
RUN  mkdir /dk/AnalyticContainer/AnalyticContainerLibrary

#setup that libraries
COPY __init__.py                                /dk/AnalyticContainer/__init__.py
COPY PentahoDIContainer/__init__.py             /dk/AnalyticContainer/PentahoDIContainer/__init__.py
COPY PentahoDIContainer/PentahoDIContainer.py   /dk/AnalyticContainer/PentahoDIContainer/PentahoDIContainer.py
COPY PentahoDIContainer/requirements.txt        /dk/AnalyticContainer/PentahoDIContainer/requirements.txt
COPY AnalyticContainerLibrary/__init__.py       /dk/AnalyticContainer/AnalyticContainerLibrary/__init__.py
COPY AnalyticContainerLibrary/ACBase.py         /dk/AnalyticContainer/AnalyticContainerLibrary/ACBase.py
COPY AnalyticContainerLibrary/ACSettings.py     /dk/AnalyticContainer/AnalyticContainerLibrary/ACSettings.py
COPY AnalyticContainerLibrary/ACSingletons.py   /dk/AnalyticContainer/AnalyticContainerLibrary/ACSingletons.py
COPY AnalyticContainerLibrary/ACPentahoDI.py    /dk/AnalyticContainer/AnalyticContainerLibrary/ACPentahoDI.py

# Set the default directory where CMD will execute
WORKDIR /dk/AnalyticContainer/PentahoDIContainer

# Install Python requirements
RUN sudo pip install -r requirements.txt

# Set the default command to execute
ENV pdi_home=$PDI_HOME/data-integration
CMD python PentahoDIContainer.py


