#@IgnoreInspection BashAddShebang
############################################################
# PythonAnaconda
# Dockerfile to build Analytic Application Containers
# Based on
############################################################

# Set the base image to Ubuntu
#
FROM debian:8.5
MAINTAINER Chris Bergh <cbergh@datakitchen.io>

#install miniconda
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git mercurial subversion

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda2-4.1.11-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh

RUN apt-get install -y curl grep sed dpkg && \
    TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
    dpkg -i tini.deb && \
    rm tini.deb && \
    apt-get clean

RUN /opt/conda/bin/conda install jupyter -y --quiet && mkdir /opt/notebooks

ENV PATH /opt/conda/bin:$PATH

# Install basic applications
RUN  apt-get install -y tar nano dialog net-tools build-essential

# Install Python and Basic Python Tools
RUN  apt-get install -y python libpq-dev python-dev python-distribute python-pip

# make a directory for the server
RUN mkdir /dk
RUN mkdir /dk/AnalyticContainer
RUN mkdir /dk/AnalyticContainer/PythonAnaconda
RUN mkdir /dk/AnalyticContainer/AnalyticContainerLibrary

#setup that libraries
COPY __init__.py                                    /dk/AnalyticContainer/__init__.py
COPY PythonAnaconda/__init__.py                     /dk/AnalyticContainer/PythonAnaconda/__init__.py
COPY PythonAnaconda/PythonAnaconda.py               /dk/AnalyticContainer/PythonAnaconda/PythonAnaconda.py
COPY PythonAnaconda/requirements.txt                /dk/AnalyticContainer/PythonAnaconda/requirements.txt
COPY AnalyticContainerLibrary/__init__.py           /dk/AnalyticContainer/AnalyticContainerLibrary/__init__.py
COPY AnalyticContainerLibrary/ACBase.py             /dk/AnalyticContainer/AnalyticContainerLibrary/ACBase.py
COPY AnalyticContainerLibrary/ACSettings.py         /dk/AnalyticContainer/AnalyticContainerLibrary/ACSettings.py
COPY AnalyticContainerLibrary/ACSingletons.py       /dk/AnalyticContainer/AnalyticContainerLibrary/ACSingletons.py
COPY AnalyticContainerLibrary/ACPythonAnaconda.py   /dk/AnalyticContainer/AnalyticContainerLibrary/ACPythonAnaconda.py

# Set the default directory where CMD will execute
WORKDIR /dk/AnalyticContainer/PythonAnaconda

# Install Python requirements
RUN pip install -r requirements.txt

ENV PYTHONPATH=/dk

# Set the default command to execute
CMD python PythonAnaconda.py

# to run the notebook
ENTRYPOINT [ "/usr/bin/tini", "--" ]
#CMD [ "/bin/bash" ]
