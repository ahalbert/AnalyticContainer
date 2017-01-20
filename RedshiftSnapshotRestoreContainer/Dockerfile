FROM ubuntu:14.04.3
MAINTAINER "Armand <armand@datakitchen.io>"

RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list
RUN apt-get update && apt-get install -y ftp wget python python-pip 
#install s3cmd
RUN wget -O- -q http://s3tools.org/repo/deb-all/stable/s3tools.key | sudo apt-key add -
RUN apt-get update && apt-get install -y s3cmd

RUN mkdir /dk
RUN mkdir /dk/AnalyticContainer
RUN mkdir /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer
RUN mkdir /dk/AnalyticContainer/AnalyticContainerLibrary

#setup that libraries
COPY RedshiftSnapshotRestoreContainer/__init__.py                                /dk/AnalyticContainer/__init__.py
COPY RedshiftSnapshotRestoreContainer/requirements.txt                           /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/requirements.txt
COPY RedshiftSnapshotRestoreContainer/RedshiftSnapshotContainer.py               /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/RedshiftSnapshotContainer.py
COPY RedshiftSnapshotRestoreContainer/make_snapshot.sh               /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/make_snapshot.sh
COPY RedshiftSnapshotRestoreContainer/delete_snapshot.sh               /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/delete_snapshot.sh
COPY RedshiftSnapshotRestoreContainer/make_cluster.sh               /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/make_cluster.sh
COPY RedshiftSnapshotRestoreContainer/make_cluster_from_snapshot.sh /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/make_cluster_from_snapshot.sh
COPY RedshiftSnapshotRestoreContainer/restore_cluster_from_snapshot.sh /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/restore_cluster_from_snapshot.sh
COPY RedshiftSnapshotRestoreContainer/delete_cluster.sh /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/delete_cluster.sh
COPY RedshiftSnapshotRestoreContainer/modify_cluster.sh /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/modify_cluster.sh
COPY AnalyticContainerLibrary/__init__.py       /dk/AnalyticContainer/AnalyticContainerLibrary/__init__.py
COPY AnalyticContainerLibrary/ACBase.py         /dk/AnalyticContainer/AnalyticContainerLibrary/ACBase.py
COPY AnalyticContainerLibrary/ACSettings.py     /dk/AnalyticContainer/AnalyticContainerLibrary/ACSettings.py
COPY AnalyticContainerLibrary/ACSingletons.py   /dk/AnalyticContainer/AnalyticContainerLibrary/ACSingletons.py

WORKDIR /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer
RUN sudo pip install -r requirements.txt
ENV PYTHONPATH=/dk
CMD python RedshiftSnapshotContainer.py
