# Welcome to Point Duty API Sink

The point duty database service is used by the Frames, Detectron and OCR API

# Files
    .
    ├── database.py
    ├── docker-compose.yaml
    ├── Dockerfile
    ├── main.py
    ├── models.py
    ├── Readme.md
    └── requirements.txt

# Setup .Env File

Place **.env** file relative to the **docker-compose.yaml**

    POINT_DUTY_ENV=development

    # credentials settings for fast-api server
    FASTAPI_LOCAL_PORT=8000
    FASTAPI_DOCKER_PORT=8000


    COMPOSE_HTTP_TIMEOUT=2000


    #MSSQL_LOCAL_HOST=192.168.0.38
    MSSQL_LOCAL_HOST=192.168.20.200

    SA_PASSWORD=2astazeY
    MSSQL_DB=point_duty
    MSSQL_ROOT_PASSWORD=7ellowEl7akey
    MSSQL_ROOT_USERNAME=Kobeissi
    MSSQL_LOCAL_PORT=1433
    MSSQL_DOCKER_PORT=1433

## Run for the first time

Open terminal relative to the **docker-compose.yml**
`$ docker-compose up --build`

**Hit on the local server**
[http://localhost:8000](http://localhost:8000)

    system=MS SQL beta
    server=point_duty
    username=Kobeissi
    password=7ellowEl7akey

## Simple Run

Run this command in the terminal
`$ docker-compose up`

## Create tables using `database/db.sql` file

    CREATE TABLE point_duty.dbo.table_1 (
        id int IDENTITY(1,1) NOT NULL,
        frame_no varchar(30) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
        video_name varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
        detectron_object text COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        ocr_object text COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        CONSTRAINT PK__table_1__3213E83F62FC9096 PRIMARY KEY (id)
    );


    -- point_duty.dbo.table_2 definition

    -- Drop table

    -- DROP TABLE point_duty.dbo.table_2;

    CREATE TABLE point_duty.dbo.table_2 (
        id int IDENTITY(1,1) NOT NULL,
        frame_no varchar(30) COLLATE Latin1_General_BIN NOT NULL,
        video_name varchar(255) COLLATE Latin1_General_BIN NOT NULL,
        file_path varchar(255) COLLATE Latin1_General_BIN NOT NULL,
        is_processed tinyint DEFAULT 0 NULL,
        is_ocr_processed tinyint DEFAULT 0 NULL,
        CONSTRAINT PK__table_2__3213E83F1E6B5C2C PRIMARY KEY (id)
    );
