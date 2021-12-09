# Welcome to Point Duty Frames API
The point duty Frames API takes the video from the relative folder and convert them into the frames and then eventually uploaded to ***minio server*** and insert the frames information into the database using the ***rds*** connection

# Files
Make sure you have to place the video into ***video_download*** folder and relative path will be like this: `video_download/file_example_MP4_1280_10MG.mp4.mp4` while giving an input

    .
    ├── database.py
    ├── docker-compose.yaml
    ├── Dockerfile
    ├── frames.py
    ├── main.py
    ├── models.py
    ├── Readme.md
    ├── requirements.txt
    └── video_download
        ├── file_example_MP4_1280_10MG.mp4.mp4



# Setup .Env File
Place **.env** file relative to the **docker-compose.yaml**

    POINT_DUTY_ENV=development

    #MSSQL_LOCAL_HOST=192.168.20.200
    MSSQL_LOCAL_HOST=192.168.20.200

    SA_PASSWORD=2astazeY
    MSSQL_DB=point_duty
    MSSQL_ROOT_PASSWORD=7ellowEl7akey
    MSSQL_ROOT_USERNAME=Kobeissi
    MSSQL_LOCAL_PORT=1433
    MSSQL_DOCKER_PORT=1433

    # credentials settings for fast-api server
    FASTAPI_LOCAL_PORT=8070
    FASTAPI_DOCKER_PORT=8000


    COMPOSE_HTTP_TIMEOUT=2000

    #minio keys setup for
    MINIO_HOST=192.168.20.200:9000
    MINIO_BUCKET_NAME=frames
    MINIO_ACCESS_KEY=Q3AM3UQ867SPQQA43P2F
    MINIO_SECRET_KEY=zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG

## Run for the first time
Open terminal relative to the **docker-compose.yml**
`$ docker-compose up --build`

Hit on the local server
[http://localhost:8070/docs](http://localhost:8070/docs)

## Simple Run
Run this command in the terminal
`$ docker-compose up`

Hit on the local server
http://localhost:8070/docs

## END POINTS

    curl -X 'GET' \
    'http://localhost:8070/upload_decord_files?file_path=video_download%2FBad_fire.mp4' \
    -H 'accept: application/json'

or

This end point takes the **relative path** of the video like this `video_download/Bad_fire.mp4` and will upload the video to **minio server** and trigger the frames codes which convert the video into frames and store the video information into **table_3** and frames information into **table_2**

    http://localhost:8070/upload_decord_files?file_path=video_download/Bad_fire.mp4

**Note:**

 * video must be place in the ***video_download*** folder