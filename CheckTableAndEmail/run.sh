#!/usr/bin/env bash

if [ "$DKROOT" == "" ]
then
	echo "DKROOT not set, exiting"
	exit 1
fi

# run ac_check_table_and_email via command line
cd $DKROOT/AnalyticContainer
pwd

# cleanup exsinng containers
echo 'cleanup exsinng containers .. ignore errors'
sudo docker rmi -f ac_check_table_and_email
sudo docker rmi -f data_ac_check_table_and_email
sudo docker rm -f ac_check_table_and_email
sudo docker rm -f data_ac_check_table_and_email
docker rm $(docker ps -a | grep ac_check_table_and_email)
docker rm $(docker ps -a | grep data_ac_check_table_and_email)


#build
echo 'building ac_check_table_and_email'
sudo docker build  -f  $DKROOT/AnalyticContainer/CheckTableAndEmail/Dockerfile -t ac_check_table_and_email .
echo 'building data_ac_check_table_and_email'
sudo docker run -d -v $DKROOT/AnalyticContainer/CheckTableAndEmail/docker-share --name="data_ac_check_table_and_email" ac_check_table_and_email:latest
echo 'adding config.json to data_ac_check_table_and_email'
sudo docker cp $DKROOT/DKModules/tests/json/check-table-send-email-container/container-node/docker-share/config.json data_ac_check_table_and_email:$DKROOT/AnalyticContainer/CheckTableAndEmail/docker-share/config.json
sudo docker cp $DKROOT/DKModules/tests/json/check-table-send-email-container/container-node/docker-share/check-table-email-template.html data_ac_check_table_and_email:$DKROOT/AnalyticContainer/CheckTableAndEmail/docker-share/check-table-email-template.html

#run
echo 'running ac_check_table_and_email'
sudo docker run -e CONTAINER_INPUT_CONFIG_FILE_PATH="$DKROOT/DKModules/tests/json/check-table-send-email-container/container-node/docker-share" -e CONTAINER_INPUT_CONFIG_FILE_NAME="config.json" -e CONTAINER_OUTPUT_PROGRESS_FILE="progress.json" -e CONTAINER_OUTPUT_LOG_FILE="ac_logger.log" -e INSIDE_CONTAINER_FILE_MOUNT="$DKROOT/AnalyticContainer/CheckTableAndEmail" -e INSIDE_CONTAINER_FILE_DIRECTORY="$DKROOT/AnalyticContainer/CheckTableAndEmail/docker-share" --volumes-from data_ac_check_table_and_email ac_check_table_and_email:latest

echo 'copying volume back .. not sure why this does not happen automatically'
sudo docker cp data_ac_check_table_and_email:$DKROOT/AnalyticContainer/CheckTableAndEmail/docker-share/progress.json $DKROOT/AnalyticContainer/CheckTableAndEmail/docker-share/progress.json
sudo docker cp data_ac_check_table_and_email:$DKROOT/AnalyticContainer/CheckTableAndEmail/docker-share/ac_logger.log $DKROOT/AnalyticContainer/CheckTableAndEmail/docker-share/ac_logger.log

sudo cat `docker inspect --format='{{(index .Mounts 0).Source}}' data_ac_check_table_and_email`/ac_logger.log | grep 'CONTAINER_STATUS_SUCCESS'
if [ $? != 0 ]
then
	exit 1
fi

echo 'completed run ac_check_table_and_email, viewing data in data_ac_check_table_and_email'
sudo ls -lGg `docker inspect --format='{{(index .Mounts 0).Source}}' data_ac_check_table_and_email` | tee output1.txt

echo 'view file system data_ac_check_table_and_email'
ls -lGg $DKROOT/AnalyticContainer/CheckTableAndEmail/docker-share/ | tee output2.txt

echo 'the two above should be the same'

diff output1.txt output2.txt

result=$?

rm output1.txt output2.txt

exit $result