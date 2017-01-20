##DataKitchen AnalyticContainer tutorial

Moving existing python code into an AnalyticContainer is simple, and does not require your code to be changed.

####Requirements for an AnalyticContainer:
 * Python class that inherits from AnalyticContainer.AnalyticContainerLibrary.ACBase 
 * Dockerfile that:
    * Sets the PYTHONPATH to include AnalyticContainerLibrary
    * Runs the python class 
    * Copies the AnalyticContainer libraries into the container
    * Copies the class that inherits into the container.
 * docker-share directory containing a config.json file
 * Node in a recipe running an AnalyticContainer
 * Container must be available on machine recipe is running on or on [Docker Hub](https://hub.docker.com)

#### Python class

Given a python file hello.py that you would like to run in an AnalyticContainer

    def hello():
        return "hello world!"
    

#### Structure of an AnalyticContainer that runs hello.py
    Dockerfile
    docker-share
        config.json
    hello.py
    AnalyticContainerTutorial.py

#### AnalyticContainerTutorial.py

This is the AnalyticContainer file then runs hello:


    from AnalyticContainer.AnalyticContainerLibrary.ACBase import *
    import hello

    class AnalyticContainerTutorial(ACBase):
        def __init__(self):
            ACBase.__init__(self)

        def execute():
            hello.hello()

    def main():
        container = MyExampleContainer()
        if container.vaild_config() is True:
            try:
                container.execute()
                container.set_container_status(CONTAINER_STATUS_SUCCESS)
            except:
                container.set_container_status(CONTAINER_STATUS_ERROR)
            container.write_log()
            container.write_progress()
        
    if __name__ == "__main__":
        main()

#### Dockerfile

    FROM ubuntu:14.04.3

    RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list
    RUN apt-get update && apt-get install -y ftp wget python python-pip 
    RUN mkdir /dk
    RUN mkdir /dk/AnalyticContainer
    RUN mkdir /dk/AnalyticContainer/AnalyticContainerTutorial
    RUN mkdir /dk/AnalyticContainer/AnalyticContainerLibrary

    COPY AnalyticContainerTutorial/hello.py /dk/AnalyticContainer/AnalyticContainerTutorial
    COPY AnalyticContainerTutorial/AnalyticContainerTutorial.py /dk/AnalyticContainer/AnalyticContainerTutorial/AnalyticContainerTutorial.py

    COPY AnalyticContainerLibrary/__init__.py       /dk/AnalyticContainer/AnalyticContainerLibrary/__init__.py
    COPY AnalyticContainerLibrary/ACBase.py         /dk/AnalyticContainer/AnalyticContainerLibrary/ACBase.py
    COPY AnalyticContainerLibrary/ACSettings.py     /dk/AnalyticContainer/AnalyticContainerLibrary/ACSettings.py
    COPY AnalyticContainerLibrary/ACSingletons.py   /dk/AnalyticContainer/AnalyticContainerLibrary/ACSingletons.py

    WORKDIR /dk/AnalyticContainer/AnalyticContainerTutorial
    CMD python AnalyticContainerTutorial.py


*NOTE*: In order to build this container, it must be run one directory above the container's folder.
*NOTE*: Do not include the docker-share folder in your Dockerfile. This is copied at runtime.

### Running an AnalyticContainer

The directory structure of the node should look like this:

    docker-share/
        config.json
    notebook.json
    description.json

#### description.json

The description file tells the recipe that this is a container

    {
        "type": "DKNode_Container",
        "description": "Optional description"
    }

#### notebook.json

The notebook.json file provides information to the recipe on how to run your container. Items in ALL CAPS must be provided by you.

    "name": "CONTAINER_NAME",
    "dockerhub-namespace": "CONTAINER_NAMESPACE",
    "dockerhub-username": "DOCKERHUB_USERNAME",
    "dockerhub-password": "DOCKERHUB_PASSWORD",
    "dockerhub-email": "DOCKERHUB_EMAIL",
    "image-repo": "CONTAINER_NAME",
    "image-tag": "CONTAINER_TAG",
    "inside-container-file-directory": "docker-share",
    "inside-container-file-mount": "/PATH/TO/ANALYTIC/CONTAINER",
    "container-input-configuration-file-path": "{{ recipename }}/NODE_NAME/docker-share",
    "container-input-configuration-file-name": "config.json",
    "container-output-log-file": "ac_logger.log",
    "container-output-progress-file": "progress.json",
    "delete-container-when-complete": true

#### docker-share/config.json
The docker-share directory moves files into the container at runtime. This allows files to be passed in without putting them into the container.  A config.json variable passes information to the AnalyticContainer at runtime. 

These are provided from ACBase in the variable `self.configuration`

    { 
        "message" : "hello"
    }

This config.json allows you to write in the Analytic Container

    ACLogger.get_logger.info(self.configuration['message'])

Inside the container, where `self.configuration['message']` will render as `'hello'`. You can also pass variables from a recipe or variation into a config.json.

### Testing outside of a recipie
The example containers provide a `run.sh` file to test your AnalyticContainer. Set the sell variable `$DKROOT` to the root directory of your workspace, and change the container references
to your container's name.
