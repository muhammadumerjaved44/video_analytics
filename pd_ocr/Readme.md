# Welcome to Point Duty OCR
The point duty ocr based on the easy ocr library

# Files
    .
    |-- Dockerfile
    |-- big.txt
    |-- database
    |   `-- 00-point-duty-mariaDB.sql
    |-- docker-compose.yaml
    |-- main.py
    |-- ocr_text_extraction.py
    |-- requirements.txt
    `-- spell_correction.py
    |-- .env



# Setup .Env File
Place **.env** file relative to the **docker-compose.yaml**

    POINT_DUTY_ENV=development

    # credentials for maria db development
    
    DB_MARIA_HOST=point-duty-mariaDB
    
    DB_MARIA_PORT=3305 # user internal port
    
    DB_MARIA_USERNAME=pd-maria
    
    DB_MARIA_PASSWORD=root
    
    # credentials for phpmyadmin
    
    PMA_HOSTS=point-duty-mariaDB
    
    PMA_USER=root
    
    PMA_PASSWORD=root
    
    PMA_LOCAL_PORT=8060
    
    PMA_DOCKER_PORT=80
    
    # credentials settings for mysql server
    
    MYSQL_ROOT_PASSWORD=root
    
    MYSQL_LOCAL_PORT=3305
    
    MYSQL_DOCKER_PORT=3306
    
    # credentials settings for redis server
    
    REDIS_LOCAL_PORT=6379
    
    REDIS_DOCKER_PORT=6379
    
    # credentials settings for deepstak server
    
    DEEPSTACK_LOCAL_PORT=5123
    
    DEEPSTACK_DOCKER_PORT=5000
    
    # credentials settings for fast-api server
    
    FASTAPI_LOCAL_PORT=8020
    
    FASTAPI_DOCKER_PORT=8000
    
    COMPOSE_HTTP_TIMEOUT=2000

## Run for the first time
Open terminal relative to the **docker-compose.yml**
`$ docker-compose up --build`

Hit on the local server  
[http://localhost:8020/docs](http://localhost:8020/docs)

## Simple Run
Run this command in the terminal
`$ docker-compose up`

Hit on the local server 
http://localhost:8020/docs


