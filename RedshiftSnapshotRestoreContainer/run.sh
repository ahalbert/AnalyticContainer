#!/usr/bin/env bash

if [ "$DKROOT" == "" ]
then
	echo "DKROOT not set, exiting"
	exit 1
fi

# run snapshot_and_restore_redshift via command line
cd $DKROOT/AnalyticContainer
pwd

# cleanup exsinng containers
echo 'cleanup existing containers .. ignore errors'
sudo docker rmi -f datakitchen/snapshot_and_restore_redshift
sudo docker rmi -f data_snapshot_and_restore_redshift
sudo docker rm -f datakitchen/snapshot_and_restore_redshift
sudo docker rm -f data_snapshot_and_restore_redshift
docker rm $(docker ps -a | grep snapshot_and_restore_redshift)
docker rm $(docker ps -a | grep data_snapshot_and_restore_redshift)

#build
echo 'building snapshot_and_restore_redshift'
sudo docker build -f $DKROOT/AnalyticContainer/RedshiftSnapshotRestoreContainer/Dockerfile -t datakitchen/snapshot_and_restore_redshift .
echo 'building redshift snapshot container'
sudo docker run -d -v /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share --name="data_snapshot_and_restore_redshift" datakitchen/snapshot_and_restore_redshift:latest
echo 'adding config.json to redshift snapshot container'
sudo docker cp $DKROOT/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share/config.json data_snapshot_and_restore_redshift:/dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share/config.json

#run
echo 'running snapshot container'
sudo docker run -e CONTAINER_INPUT_CONFIG_FILE_PATH="$DKROOT/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share" -e CONTAINER_INPUT_CONFIG_FILE_NAME="config.json" -e CONTAINER_OUTPUT_PROGRESS_FILE="progress.json" -e CONTAINER_OUTPUT_LOG_FILE="ac_logger.log" -e INSIDE_CONTAINER_FILE_MOUNT="/dk/AnalyticContainer/RedshiftSnapshotRestoreContainer" -e INSIDE_CONTAINER_FILE_DIRECTORY="/dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share" --volumes-from data_snapshot_and_restore_redshift datakitchen/snapshot_and_restore_redshift:latest
sudo docker cp data_snapshot_and_restore_redshift:/dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share/progress.json $DKROOT/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share/progress.json
sudo docker cp data_snapshot_and_restore_redshift:/dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share/ac_logger.log $DKROOT/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share/ac_logger.log

echo 'completed run data_snapshot_and_restore_redshift, viewing data in data_snapshot_and_restore_redshift'
sudo ls -lGg `docker inspect --format='{{(index .Mounts 0).Source}}' data_snapshot_and_restore_redshift` | tee output1.txt

echo 'view file system data_snapshot_and_restore_redshift'
ls -lGg $DKROOT/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share/ | tee output2.txt

echo 'Note: the two above should be the same'

diff output1.txt output2.txt

result=$?

rm output1.txt output2.txt

exit $result
