# Welcome to Point Duty Detectron2 API
The point duty **Detectron2 API** takes the ***un-processed*** files information from the ***table_2*** and make predictions against the frames which are not processed and returns the object that contains the predictions. these predictions are then saved into the ***table_1*** in the column ***detectron_object*** and also it will update the column ***is_processed*** from **0 to 1** so that that frame will not be processed again

# Files
The folder containing the following files

    .
    ├── database.py
    ├── detectron.py
    ├── docker-compose.yaml
    ├── Dockerfile
    ├── main.py
    ├── models.py
    ├── pdPredict.py
    ├── Readme.md
    └── requirements.txt



# Setup .Env File
Place **.env** file relative to the **docker-compose.yaml**

    POINT_DUTY_ENV=development

    DOCKER_ENABLE=True

    # credentials settings for fast-api server
    FASTAPI_LOCAL_PORT=8060
    FASTAPI_DOCKER_PORT=8000


    COMPOSE_HTTP_TIMEOUT=2000

    APP_AUTH_TOKEN=2oOPf-LiEF6HP85f1xJ_OA08pYDOgMLLTD7myqPoJ-w
    SKIP_AUTH=0


    #MSSQL_LOCAL_HOST=192.168.0.38
    MSSQL_LOCAL_HOST=192.168.20.200

    SA_PASSWORD=2astazeY
    MSSQL_DB=point_duty
    MSSQL_ROOT_PASSWORD=7ellowEl7akey
    MSSQL_ROOT_USERNAME=Kobeissi
    MSSQL_LOCAL_PORT=1433
    MSSQL_DOCKER_PORT=1433

    #minio setup keys
    MINIO_HOST=192.168.20.200:9000
    MINIO_BUCKET_NAME=frames
    MINIO_ACCESS_KEY=Q3AM3UQ867SPQQA43P2F
    MINIO_SECRET_KEY=zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG


## Run for the first time
Open terminal relative to the **docker-compose.yml**
`$ docker-compose up --build`

Hit on the local server
[http://localhost:8060/docs](http://localhost:8060/docs)

## Simple Run
Run this command in the terminal
`$ docker-compose up`

Hit on the local server
http://localhost:8060/docs