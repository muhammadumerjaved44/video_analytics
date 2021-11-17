# Welcome to Point Duty MINO Service

The point duty MINIO service is just like S3 Bucket but on the local enviorment. The services is used by the Frames API, Detectron and OCR

Frame API takes video as an input and convert the video into frames and these frames will be uploaded to the ***minio*** server and frames information will be written to the tables

# Files
    .
    ├── docker-compose.yaml
    ├── nginx.conf
    └── Readme.md

# Setup .Env File

Place **.env** file relative to the **docker-compose.yaml**

    POINT_DUTY_ENV=development

    # credentials settings for fast-api server
    FASTAPI_LOCAL_PORT=9000
    FASTAPI_DOCKER_PORT=8000


    COMPOSE_HTTP_TIMEOUT=2000


    #minio keys setup for
    MINIO_ROOT_USER=Q3AM3UQ867SPQQA43P2F
    MINIO_ROOT_PASSWORD=zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG
    MINIO_MAIN_PORT=9000
    MINIO_SECOENDRY_PORT=9001



## Run for the first time
Open terminal relative to the **docker-compose.yml**
`$ docker-compose up --build`

**Hit on the local server**
You can login by using the same keys from the GUI interface
[http://localhost:9000](http://localhost:9000)

    username = Q3AM3UQ867SPQQA43P2F
    password = zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG

## Simple Run
Run this command in the terminal
`$ docker-compose up`