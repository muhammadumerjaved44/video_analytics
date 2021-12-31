# Welcome to Point Duty RDS Service

The point duty database service is used by the Frames, Detectron and OCR API

# Files
    .
    ├── configure-db.sh
    ├── database
    │   └── db.sql
    ├── docker-compose.yml
    ├── Dockerfile
    ├── entrypoint.sh
    ├── Readme.md
    └── setup.sql

# Setup .Env File

Place **.env** file relative to the **docker-compose.yaml**

    POINT_DUTY_ENV=development

    # credentials settings for mssql server
    SA_PASSWORD=2astazeY
    MSSQL_DB=point_duty
    MSSQL_ROOT_PASSWORD=7ellowEl7akey
    MSSQL_ROOT_USERNAME=Kobeissi
    MSSQL_LOCAL_PORT=1433
    MSSQL_DOCKER_PORT=1433

    # adminer port for mssql server

    ADMINER_LOCAL_PORT=8080
    ADMINER_DOCKER_PORT=8080

    # credentials settings for redis server
    REDIS_LOCAL_PORT=6379
    REDIS_DOCKER_PORT=6379


## Run for the first time
Open terminal relative to the **docker-compose.yml**
`$ docker-compose up --build`

**Hit on the local server**
[http://localhost:8080](http://localhost:8080)

    system=MS SQL beta
    server=point_duty
    username=Kobeissi
    password=7ellowEl7akey

## Simple Run
Run this command in the terminal
`$ docker-compose up`

## Create tables using `database/db.sql` file

    -- DROP SCHEMA dbo;

    --CREATE SCHEMA dbo;
    -- point_duty.dbo.table_3 definition

    -- Drop table

    -- DROP TABLE point_duty.dbo.table_3;

    CREATE TABLE point_duty.dbo.table_3 (
        id bigint IDENTITY(1,1) NOT NULL,
        video_name varchar(255) COLLATE Latin1_General_BIN NOT NULL,
        version_id varchar(100) COLLATE Latin1_General_BIN NOT NULL,
        is_video_processed tinyint DEFAULT 0 NULL,
        is_in_progress tinyint DEFAULT 0 NULL,
        video_url text COLLATE Latin1_General_BIN NOT NULL,
        CONSTRAINT PK_26 PRIMARY KEY (id)
    );


    -- point_duty.dbo.table_2 definition

    -- Drop table

    -- DROP TABLE point_duty.dbo.table_2;

    CREATE TABLE point_duty.dbo.table_2 (
        id bigint IDENTITY(0,1) NOT NULL,
        video_id bigint NOT NULL,
        frame_no varchar(255) COLLATE Latin1_General_BIN NOT NULL,
        video_name varchar(255) COLLATE Latin1_General_BIN NOT NULL,
        file_path text COLLATE Latin1_General_BIN NOT NULL,
        is_processed tinyint DEFAULT 0 NULL,
        is_ocr_processed tinyint DEFAULT 0 NULL,
        is_pic_purified tinyint DEFAULT 0 NULL,
        is_qr_processed tinyint DEFAULT 0 NULL,
        CONSTRAINT PK_24 PRIMARY KEY (id,video_id),
        CONSTRAINT FK_94 FOREIGN KEY (video_id) REFERENCES point_duty.dbo.table_3(id)
    );
    CREATE NONCLUSTERED INDEX FK_96 ON dbo.table_2 (  video_id ASC  )
        WITH (  PAD_INDEX = OFF ,FILLFACTOR = 100  ,SORT_IN_TEMPDB = OFF , IGNORE_DUP_KEY = OFF , STATISTICS_NORECOMPUTE = OFF , ONLINE = OFF , ALLOW_ROW_LOCKS = ON , ALLOW_PAGE_LOCKS = ON  )
        ON [PRIMARY ] ;


    -- point_duty.dbo.table_1 definition

    -- Drop table

    -- DROP TABLE point_duty.dbo.table_1;

    CREATE TABLE point_duty.dbo.table_1 (
        id bigint IDENTITY(0,1) NOT NULL,
        frame_id bigint NOT NULL,
        video_id bigint NOT NULL,
        frame_no varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
        video_name varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
        object_ varchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        attribute_ varchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        value_ text COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        CONSTRAINT PK__table_1__3213E83F62FC9096 PRIMARY KEY (id,frame_id,video_id),
        CONSTRAINT FK_85 FOREIGN KEY (frame_id,video_id) REFERENCES point_duty.dbo.table_2(id,video_id)
    );
    CREATE NONCLUSTERED INDEX FK_88 ON dbo.table_1 (  frame_id ASC  , video_id ASC  )
        WITH (  PAD_INDEX = OFF ,FILLFACTOR = 100  ,SORT_IN_TEMPDB = OFF , IGNORE_DUP_KEY = OFF , STATISTICS_NORECOMPUTE = OFF , ONLINE = OFF , ALLOW_ROW_LOCKS = ON , ALLOW_PAGE_LOCKS = ON  )
        ON [PRIMARY ] ;
