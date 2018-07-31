# Getting Up and Running

1. If you want your own geospatial datasets to be uploaded to girder, create a directory called "data" in this directory. Make sure you copy your files to the data directory.

    ```sh
    mkdir data
    cp path/to/my/geospatial/datasets/* data/
    ```

2. Start the services by running docker-compose up.
    ```sh
	docker-compose build --no-cache
    docker-compose up
    ```

    This will get mongodb, rabbitmq, girder and girder_worker containers up and running. Both girder and girder_worker will     have necessary plugins/tasks installed by the entrypoint script.

3. Navigate to http://localhost:8989 to see your girder instance with your data uploaded to it.

4. An admin user will be created for you with a default password. Authenticate girder with your credentials.
    - username: admin
	- password: letmein

   It is a good idea to change the default password at some point.
