#!/usr/bin/env bash

if [ "$DKROOT" == "" ]
then
	echo "DKROOT not set, exiting"
	exit 1
fi
# run ac_postgres_container via command line
cd $DKROOT/AnalyticContainer
pwd

# cleanup exsinng containers
echo 'cleanup exsiting containers .. ignore errors'
sudo docker rmi -f ac_postgres_container
sudo docker rmi -f data_ac_postgres_container
sudo docker rm -f ac_postgres_container
sudo docker rm -f data_ac_postgres_container
sudo docker rm $(docker ps -a | grep ac_postgres_container)
sudo docker rm $(docker ps -a | grep data_ac_postgres_container)


#build
echo 'building ac_postgres_container'
sudo docker build  -f  $DKROOT/AnalyticContainer/PostgresContainer/Dockerfile -t ac_postgres_container .
echo 'building data_ac_postgres_container'
sudo docker run -d -v $DKROOT/AnalyticContainer/PostgresContainer/docker-share --name="data_ac_postgres_container" ac_postgres_container:latest
echo 'adding config.json to data_ac_postgres_container'
sudo docker cp $DKROOT/DKModules/tests/json/postgres-container/container-node/docker-share/config.json data_ac_postgres_container:$DKROOT/AnalyticContainer/PostgresContainer/docker-share/config.json

#run
echo 'running ac_postgres_container'
sudo docker run -e CONTAINER_INPUT_CONFIG_FILE_PATH="$DKROOT/DKModules/tests/json/postgres-container/container-node/docker-share" -e CONTAINER_INPUT_CONFIG_FILE_NAME="config.json" -e CONTAINER_OUTPUT_PROGRESS_FILE="progress.json" -e CONTAINER_OUTPUT_LOG_FILE="ac_logger.log" -e INSIDE_CONTAINER_FILE_MOUNT="$DKROOT/AnalyticContainer/PostgresContainer" -e INSIDE_CONTAINER_FILE_DIRECTORY="$DKROOT/AnalyticContainer/PostgresContainer/docker-share" --volumes-from data_ac_postgres_container ac_postgres_container:latest

echo 'copying volume back .. not sure why this does not happen automatically'
sudo docker cp data_ac_postgres_container:$DKROOT/AnalyticContainer/PostgresContainer/docker-share/progress.json $DKROOT/AnalyticContainer/PostgresContainer/docker-share/progress.json
sudo docker cp data_ac_postgres_container:$DKROOT/AnalyticContainer/PostgresContainer/docker-share/ac_logger.log $DKROOT/AnalyticContainer/PostgresContainer/docker-share/ac_logger.log

echo 'completed run ac_postgres_container, viewing data in data_ac_postgres_container' 
sudo ls -lGg `docker inspect --format='{{(index .Mounts 0).Source}}' data_ac_postgres_container` | tee output1.txt
sudo cat `docker inspect --format='{{(index .Mounts 0).Source}}' data_ac_postgres_container`/ac_logger.log | grep 'CONTAINER_STATUS_SUCCESS'

if [ $? != 0 ]
then
	exit 1
fi

sudo cat `docker inspect --format='{{(index .Mounts 0).Source}}' data_ac_postgres_container`/progress.json | grep '"container-return-status": "completed_success"'

if [ $? != 0 ]
then
	exit 1
fi

echo 'view file system data_ac_postgres_container'
ls -lGg $DKROOT/AnalyticContainer/PostgresContainer/docker-share/ | tee output2.txt

echo 'the two above should be the same'

diff output1.txt output2.txt

result=$?

rm output1.txt output2.txt

exit $result