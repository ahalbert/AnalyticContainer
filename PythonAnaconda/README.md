# PythonAnaconda Example Container DIRECTIONS
 
 * in dir:   /dk/AnalyticContainers directory

 * build :                   ``` sudo docker build  -f PythonAnaconda/Dockerfile -t ac_python_anaconda . ```
 *(or forced re-build):     ``` sudo docker build  -f PythonAnaconda/Dockerfile --no-cache -t ac_python_anaconda . ```

 * create data container:    ``` sudo docker run -d -v /dk/AnalyticContainer/PythonAnaconda/docker-share --name="data_ac_python_anaconda" ac_python_anaconda:latest ```
 * add config file:          ``` sudo docker cp  /dk/AnalyticContainer/PythonAnaconda/docker-share/config.json data_ac_python_anaconda:/dk/AnalyticContainer/PythonAnaconda/docker-share/config.json ```
 * run:                      
 ``` 
 sudo docker run -e CONTAINER_INPUT_CONFIG_FILE_PATH=" /dk/AnalyticContainer/PythonAnaconda/docker-share" -e CONTAINER_INPUT_CONFIG_FILE_NAME="config.json" -e CONTAINER_OUTPUT_PROGRESS_FILE="progress.json" -e CONTAINER_OUTPUT_LOG_FILE="ac_logger.log" -e INSIDE_CONTAINER_FILE_MOUNT="/dk/AnalyticContainer/PythonAnaconda" -e INSIDE_CONTAINER_FILE_DIRECTORY="/dk/AnalyticContainer/PythonAnaconda/docker-share" --volumes-from data_ac_python_anaconda ac_python_anaconda:latest
 ```
 
 * copy data back:           ``` sudo docker cp data_ac_python_anaconda:/dk/AnalyticContainer/PythonAnaconda/docker-share/progress.json /dk/AnalyticContainer/PythonAnaconda/docker-share/progress.json ```
                             ``` sudo docker cp data_ac_python_anaconda:/dk/AnalyticContainer/PythonAnaconda/docker-share/ac_logger.log /dk/AnalyticContainer/PythonAnaconda/docker-share/ac_logger.log ```

 * see in data container:    ``` sudo ls -al `docker inspect --format='{{(index .Mounts 0).Source}}' data_ac_python_anaconda`  ```

### cleanup containers
```
         docker rm $(docker ps -a -q)
         docker rm $(docker ps -a | grep ac_python_anaconda) 
         docker rm $(docker ps -a | grep data_ac_python_anaconda) 
```
### cleanup images (you may have to cleanup containers first)
```         
         docker rmi $(docker images | grep ac_python_anaconda) 
```
### cleanup stranded volumes:  https://github.com/chadoe/docker-cleanup-volumes
```
         docker run -v /var/run/docker.sock:/var/run/docker.sock -v /var/lib/docker:/var/lib/docker --rm martin/docker-cleanup-volumes
         look in 'sudo ls -al /var/lib/docker/volumes/'
```
### run the Juypter UI
```
         docker run -i -t -p 8888:8888 ac_python_anaconda /bin/bash -c "/opt/conda/bin/jupyter notebook --notebook-dir=/opt/notebooks --ip='*' --port=8888 --no-browser"
```

### other commands (FYI)
 * run in bash:     ``` sudo docker run -e AC_FILE_MOUNT="/mnt/docker-share" -it ac_python_anaconda:latest /bin/bash ```
 
### push to docker hub
 1. login            ``` sudo docker login ```
 2. list images      ``` docker images ```
 3. tag              ``` docker tag <image ID> datakitchen/ac_python_anaconda:latest ```
 4. push             ``` docker push datakitchen/ac_python_anaconda:latest ```
 

