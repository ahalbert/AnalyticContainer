#!/usr/bin/env bash

if [ "$DKROOT" == "" ]
then
	echo "DKROOT not set, exiting"
	exit 1

fi
# run ac_python_anaconda via command line
cd $DKROOT/AnalyticContainer
pwd

# cleanup exsinng containers
echo 'cleanup exsiting containers .. ignore errors'
sudo docker rmi -f ac_python_anaconda
sudo docker rmi -f data_ac_python_anaconda
sudo docker rm -f ac_python_anaconda
sudo docker rm -f data_ac_python_anaconda
sudo docker rm $(docker ps -a | grep ac_python_anaconda)
sudo docker rm $(docker ps -a | grep data_ac_python_anaconda)


#build
echo 'building ac_python_anaconda'
sudo docker build -f $DKROOT/AnalyticContainer/PythonAnaconda/Dockerfile -t ac_python_anaconda .
echo 'building data_ac_python_anaconda'
sudo docker run -d -v \
    $DKROOT/AnalyticContainer/PythonAnaconda/docker-share \
    --name="data_ac_python_anaconda" ac_python_anaconda:latest
echo 'adding config.json to data_ac_python_anaconda'
sudo docker cp \
    $DKROOT/DKDemoCustomer/dc/templates/agile-analytic-ops/pythonanaconda-segment/actions/docker-share/config.json \
    data_ac_python_anaconda:$DKROOT/AnalyticContainer/PythonAnaconda/docker-share/config.json
    echo 'adding python_default.ipynb to data_ac_python_anaconda'
sudo docker cp \
    $DKROOT/DKDemoCustomer/dc/templates/agile-analytic-ops/pythonanaconda-segment/actions/docker-share/test_notebook.ipynb \
    data_ac_python_anaconda:$DKROOT/AnalyticContainer/PythonAnaconda/docker-share/test_notebook.ipynb

#run
echo 'running ac_python_anaconda'
sudo docker run \
    -e CONTAINER_INPUT_CONFIG_FILE_PATH="$DKROOT/DKDemoCustomer/dc/templates/agile-analytic-ops/pythonanaconda-segment/actions/docker-share" \
    -e CONTAINER_INPUT_CONFIG_FILE_NAME="config.json" \
    -e CONTAINER_OUTPUT_PROGRESS_FILE="progress.json"\
    -e CONTAINER_OUTPUT_LOG_FILE="ac_logger.log" \
    -e INSIDE_CONTAINER_FILE_MOUNT="$DKROOT/AnalyticContainer/PythonAnaconda" \
    -e INSIDE_CONTAINER_FILE_DIRECTORY="$DKROOT/AnalyticContainer/PythonAnaconda/docker-share" \
    --volumes-from data_ac_python_anaconda ac_python_anaconda:latest

echo 'copying volume back .. not sure why this does not happen automatically'
sudo docker cp \
    data_ac_python_anaconda:$DKROOT/AnalyticContainer/PythonAnaconda/docker-share/progress.json \
    $DKROOT/DKDemoCustomer/dc/templates/agile-analytic-ops/pythonanaconda-segment/actions/docker-share/progress.json
sudo docker cp \
    data_ac_python_anaconda:$DKROOT/AnalyticContainer/PythonAnaconda/docker-share/ac_logger.log \
    $DKROOT/DKDemoCustomer/dc/templates/agile-analytic-ops/pythonanaconda-segment/actions/docker-share/ac_logger.log

echo 'completed run ac_python_anaconda, viewing data in data_ac_python_anaconda'
sudo ls -lGg `docker inspect --format='{{(index .Mounts 0).Source}}' data_ac_python_anaconda` | tee output1.txt
sudo cat `docker inspect --format='{{(index .Mounts 0).Source}}' data_ac_python_anaconda`/ac_logger.log
sudo cat `docker inspect --format='{{(index .Mounts 0).Source}}' data_ac_python_anaconda`/progress.json

echo 'view file system data_ac_python_anaconda'
ls -lGg $DKROOT/DKDemoCustomer/dc/templates/agile-analytic-ops/pythonanaconda-segment/actions/docker-share | tee output2.txt

echo 'the two above should be the same'

diff output1.txt output2.txt

result=$?

rm output1.txt output2.txt

exit $result