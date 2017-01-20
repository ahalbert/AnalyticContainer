#!/usr/bin/env bash

if [ "$DKROOT" == "" ]
then
	echo "DKROOT not set, exiting"
	exit 1
fi

# run ac_pentahodi_container via command line
cd $DKROOT/AnalyticContainer
pwd

# cleanup exsinng containers  docker rm $(docker ps -q -f status=exited)
echo 'cleanup existng containers .. ignore errors'

sudo docker rmi -f ac_pentahodi_container
sudo docker rmi -f data_ac_pentahodi
sudo docker rm -f ac_pentahodi_container
sudo docker rm -f data_ac_pentahodi
sudo docker rm $(docker ps -a | grep ac_pentahodi_container)
sudo docker rm $(docker ps -a | grep data_ac_pentahodi)


#build
echo 'building ac_pentahodi_container'
sudo docker build -f $DKROOT/AnalyticContainer/PentahoDIContainer/Dockerfile -t ac_pentahodi_container .
echo 'building data_ac_pentahodi'
sudo docker run -d -v $DKROOT/AnalyticContainer/PentahoDIContainer/docker-share --name="data_ac_pentahodi" ac_pentahodi_container:latest
echo 'adding config.json to data_ac_pentahodi'
sudo docker cp $DKROOT/DKModules/tests/json/pentahodi-container/pentahodi-container-action-node/actions/docker-share/config.json data_ac_pentahodi:$DKROOT/AnalyticContainer/PentahoDIContainer/docker-share/config.json
sudo docker cp $DKROOT/DKModules/tests/json/pentahodi-container/pentahodi-container-action-node/actions/docker-share/pentaho-test.ktr data_ac_pentahodi:$DKROOT/AnalyticContainer/PentahoDIContainer/docker-share/pentaho-test.ktr

#run
echo 'running ac_pentahodi_container'
sudo docker run -e CONTAINER_INPUT_CONFIG_FILE_PATH="$DKROOT/DKModules/tests/json/pentahodi-container/pentahodi-container-action-node/docker-share/DKDataSource_Container.json" -e CONTAINER_INPUT_CONFIG_FILE_NAME="config.json" -e CONTAINER_OUTPUT_PROGRESS_FILE="progress.json" -e CONTAINER_OUTPUT_LOG_FILE="ac_logger.log" -e INSIDE_CONTAINER_FILE_MOUNT="$DKROOT/AnalyticContainer/PentahoDIContainer" -e INSIDE_CONTAINER_FILE_DIRECTORY="$DKROOT/AnalyticContainer/PentahoDIContainer/docker-share" --volumes-from data_ac_pentahodi ac_pentahodi_container:latest

echo 'copying volume back .. not sure why this does not happen automatically'
sudo docker cp data_ac_pentahodi:$DKROOT/AnalyticContainer/PentahoDIContainer/docker-share/progress.json $DKROOT/AnalyticContainer/PentahoDIContainer/docker-share/progress.json
sudo docker cp data_ac_pentahodi:$DKROOT/AnalyticContainer/PentahoDIContainer/docker-share/ac_logger.log $DKROOT/AnalyticContainer/PentahoDIContainer/docker-share/ac_logger.log

echo 'completed run ac_pentahodi_container, viewing data in data_ac_pentahodi'
sudo ls -lGg `docker inspect --format='{{(index .Mounts 0).Source}}' data_ac_pentahodi` | tee output1.txt
sudo cat `docker inspect --format='{{(index .Mounts 0).Source}}' data_ac_pentahodi`/ac_logger.log
sudo cat `docker inspect --format='{{(index .Mounts 0).Source}}' data_ac_pentahodi`/progress.json

echo 'view file system data_ac_pentahodi'
ls -lGg $DKROOT/AnalyticContainer/PentahoDIContainer/docker-share/ | tee output2.txt

echo 'the two above should be the same'

diff output1.txt output2.txt

result=$?

rm output1.txt output2.txt

exit $result