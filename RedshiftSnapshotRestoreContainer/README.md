# RedshiftSnapshotContainer Example Container DIRECTIONS
 
 *in dir:   /dk/AnalyticContainers directory

 *build :                   ``` sudo docker build  -f /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/Dockerfile -t datakitchen/snapshot_and_restore_redshift . ```
 *(or forced re-build):     ``` sudo docker build  -f /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/Dockerfile --no-cache -t datakitchen/snapshot_and_restore_redshift . ```

 * create data container:    ``` sudo docker run -d -v /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share --name="data_snapshot_and_restore_redshift" datakitchen/snapshot_and_restore_redshift:latest ```
 * add config file:          ``` sudo docker cp  /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share/config.json data_snapshot_and_restore_redshift:/dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share/config.json ```
 * run:                      
 ``` 
 sudo docker run -e CONTAINER_INPUT_CONFIG_FILE_PATH="/dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share" -e CONTAINER_INPUT_CONFIG_FILE_NAME="config.json" -e CONTAINER_OUTPUT_PROGRESS_FILE="progress.json" -e CONTAINER_OUTPUT_LOG_FILE="ac_logger.log" -e INSIDE_CONTAINER_FILE_MOUNT="/dk/AnalyticContainer/RedshiftSnapshotRestoreContainer" -e INSIDE_CONTAINER_FILE_DIRECTORY="/dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share" --volumes-from data_snapshot_and_restore_redshift datakitchen/snapshot_and_restore_redshift:latest
 ```
 
 
 * copy data back:           ``` sudo docker cp data_snapshot_and_restore_redshift:/dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share/progress.json /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share/progress.json ```
                             ``` sudo docker cp data_snapshot_and_restore_redshift:/dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share/ac_logger.log /dk/AnalyticContainer/RedshiftSnapshotRestoreContainer/docker-share/ac_logger.log ```

 * see in data container:    ``` sudo ls -al `docker inspect --format='{{(index .Mounts 0).Source}}' data_snapshot_and_restore_redshift`  ```

## cleanup containers
```
         docker rm $(docker ps -a -q)
         docker rm $(docker ps -a | grep datakitchen/snapshot_and_restore_redshift) 
         docker rm $(docker ps -a | grep data_snapshot_and_restore_redshift) 
```
## cleanup stranded volumes:  https://github.com/chadoe/docker-cleanup-volumes
```
         docker run -v /var/run/docker.sock:/var/run/docker.sock -v /var/lib/docker:/var/lib/docker --rm martin/docker-cleanup-volumes
         look in 'sudo ls -al /var/lib/docker/volumes/'
```
## other commands (FYI)
 * run in bash:     ``` sudo docker run -e AC_FILE_MOUNT="/mnt/docker-share" -it datakitchen/snapshot_and_restore_redshift:latest /bin/bash ```
 
## push to docker hub
 1. login            ``` sudo docker login ```
 2. list images      ``` docker images ```
 3. tag              ``` docker tag <image ID> datakitchen/snapshot_and_restore_redshift:latest ```
 4. push             ``` docker push datakitchen/snapshot_and_restore_redshift:latest ```
 

