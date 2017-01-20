#!/usr/bin/env bash

if [ "$DKROOT" == "" ]
then
	echo "DKROOT not set, exiting"
	exit 1
fi
# run ac_container_vault_test via command line
cd $DKROOT/AnalyticContainer
pwd

# cleanup exsinng containers
echo 'cleanup exsinng containers .. ignore errors'
sudo docker rmi -f ac_vault_test
sudo docker rmi -f data_ac_vault_test
sudo docker rm -f ac_vault_test
sudo docker rm -f data_ac_vault_test
docker rm $(docker ps -a | grep ac_container_vault_test)
docker rm $(docker ps -a | grep data_ac_vault_test)


#build
echo 'building ac_container_vault_test'
sudo docker build -f $DKROOT/AnalyticContainer/ACVaultTest/Dockerfile -t ac_vault_test .
echo 'building data_ac_vault_test'
sudo docker run -d -v $DKROOT/AnalyticContainer/ACVaultTest/docker-share --name="data_ac_vault_test" ac_vault_test:latest
echo 'adding config.json to data_ac_vault_test'
sudo docker cp $DKROOT/AnalyticContainer/ACVaultTest/docker-share/config.json data_ac_vault_test:$DKROOT/AnalyticContainer/ACVaultTest/docker-share/config.json

#run
echo 'running ac_vault_test'
sudo docker run -e CONTAINER_INPUT_CONFIG_FILE_PATH="$DKROOT/AnalyticContainer/ACVaultTest/docker-share" -e CONTAINER_INPUT_CONFIG_FILE_NAME="config.json" -e CONTAINER_OUTPUT_PROGRESS_FILE="progress.json" -e CONTAINER_OUTPUT_LOG_FILE="dk_logger.log" -e INSIDE_CONTAINER_FILE_MOUNT="$DKROOT/AnalyticContainer/ACVaultTest" -e INSIDE_CONTAINER_FILE_DIRECTORY="$DKROOT/AnalyticContainer/ACVaultTest/docker-share" --volumes-from data_ac_vault_test ac_vault_test:latest
sudo docker cp data_ac_vault_test:$DKROOT/AnalyticContainer/ACVaultTest/docker-share/progress.json $DKROOT/AnalyticContainer/ACVaultTest/docker-share/progress.json
sudo docker cp data_ac_vault_test:$DKROOT/AnalyticContainer/ACVaultTest/docker-share$DKROOT_logger.log $DKROOT/AnalyticContainer/ACVaultTest/docker-share$DKROOT_logger.log

echo 'completed run data_ac_vault_test, viewing data in data_ac_vault_test'
sudo ls -lGg `docker inspect --format='{{(index .Mounts 0).Source}}' data_ac_vault_test` | tee output1.txt

echo 'view file system data_ac_vault_test'
ls -lGg $DKROOT/AnalyticContainer/ACVaultTest/docker-share/ | tee output2.txt

echo 'Note: the two above should be the same'

diff output1.txt output2.txt

result=$?

rm output1.txt output2.txt

exit $result