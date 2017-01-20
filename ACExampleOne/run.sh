#!/usr/bin/env bash

if [ "$DKROOT" == "" ]
then
	echo "DKROOT not set, exiting"
	exit 1
fi

# run ac_container_example_one via command line
cd $DKROOT/AnalyticContainer

# cleanup exsinng containers
echo 'cleanup exsinng containers .. ignore errors'
sudo docker rmi -f ac_container_example_one
sudo docker rmi -f data_ac_example_one
sudo docker rm -f ac_container_example_one
sudo docker rm -f data_ac_example_one
docker rm $(docker ps -a | grep ac_container_example_one)
docker rm $(docker ps -a | grep data_ac_example_one)

#build
echo 'building ac_container_example_one'
sudo docker build -f $DKROOT/AnalyticContainer/ACExampleOne/Dockerfile -t ac_container_example_one .
echo 'building data_ac_example_one'
sudo docker run -d -v $DKROOT/AnalyticContainer/ACExampleOne/docker-share --name="data_ac_example_one" ac_container_example_one:latest
echo 'adding config.json to data_ac_example_one'
sudo docker cp $DKROOT/AnalyticContainer/ACExampleOne/docker-share/config.json data_ac_example_one:$DKROOT/AnalyticContainer/ACExampleOne/docker-share/config.json

#run
echo 'running ac_example_one'
sudo docker run -e CONTAINER_INPUT_CONFIG_FILE_PATH="$DKROOT/AnalyticContainer/ACExampleOne/docker-share" -e CONTAINER_INPUT_CONFIG_FILE_NAME="config.json" -e CONTAINER_OUTPUT_PROGRESS_FILE="progress.json" -e CONTAINER_OUTPUT_LOG_FILE="ac_logger.log" -e INSIDE_CONTAINER_FILE_MOUNT="$DKROOT/AnalyticContainer/ACExampleOne" -e INSIDE_CONTAINER_FILE_DIRECTORY="$DKROOT/AnalyticContainer/ACExampleOne/docker-share" --volumes-from data_ac_example_one ac_container_example_one:latest
sudo docker cp data_ac_example_one:$DKROOT/AnalyticContainer/ACExampleOne/docker-share/progress.json $DKROOT/AnalyticContainer/ACExampleOne/docker-share/progress.json
sudo docker cp data_ac_example_one:$DKROOT/AnalyticContainer/ACExampleOne/docker-share/ac_logger.log $DKROOT/AnalyticContainer/ACExampleOne/docker-share/ac_logger.log

echo 'completed run data_ac_example_one, viewing data in data_ac_example_one'
sudo ls -lGg `docker inspect --format='{{(index .Mounts 0).Source}}' data_ac_example_one` | tee output1.txt

echo 'view file system data_ac_example_one'
ls -lGg $DKROOT/AnalyticContainer/ACExampleOne/docker-share/ | tee output2.txt

echo 'Note: the two above should be the same'

diff output1.txt output2.txt

result=$?

rm output1.txt output2.txt

exit $result
