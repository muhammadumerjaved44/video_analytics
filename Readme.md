# Welcome to Point Duty ***Analytics Procject***
This project Containes the three APIs which are as follows
* **Frames API**
* **Detectron API**
* **OCR API**

#### Dependency

Its requires these following servieses to run properly

* **Minio Server**
* **Relational Database Server - RDS (MS-SQL)**
* **Video Search Engine Server - VSE**

Note: For better experience use **VS-Code IDE**

#### Other Requirments
* **Python 3.8 - Anaconda Recommended**
* **Docker & Docker Compose - for Linux**
* **Docker Desktop - for Win user**
* **MS-SQL Server or Dbeaver-CE**


## How to run the Project

### Step 1

After cloning your project, Open your terminal like this

    ~/rndenrichmentmicroservices$

Type code .

    ~/rndenrichmentmicroservices$code .

it will open vs code and directory structure will be like this

    .
    ├── pd_detectron2
    │   ├── database.py
    │   ├── detectron.py
    │   ├── docker-compose.yaml
    │   ├── Dockerfile
    │   ├── main.py
    │   ├── models.py
    │   ├── pdPredict.py
    │   ├── Readme.md
    │   ├── requirements.txt
    ├── pd_frames
    │   ├── database.py
    │   ├── docker-compose.yaml
    │   ├── Dockerfile
    │   ├── frames.py
    │   ├── main.py
    │   ├── models.py
    │   ├── Readme.md
    │   ├── requirements.txt
    │   └── video_download
    │       ├── Bad_fire.mp4
    │       ├── file_example_MP4_1280_10MG.mp4
    ├── pd_minio
    │   ├── docker-compose.yaml
    │   ├── nginx.conf
    │   └── Readme.md
    ├── pd_ocr
    │   ├── big.txt
    │   ├── database.py
    │   ├── docker-compose.yaml
    │   ├── Dockerfile
    │   ├── main.py
    │   ├── models.py
    │   ├── ocr.py
    │   ├── Readme.html
    │   ├── Readme.md
    │   ├── requirements.txt
    │   └── spell_correction.py
    ├── pd_rds
    │   ├── configure-db.sh
    │   ├── database
    │   │   └── db.sql
    │   ├── docker-compose.yml
    │   ├── Dockerfile
    │   ├── entrypoint.sh
    │   ├── Readme.md
    │   └── setup.sql
    ├── pd_vse
    │   ├── database.py
    │   ├── docker-compose.yaml
    │   ├── Dockerfile
    │   ├── main.py
    │   ├── models.py
    │   ├── Readme.md
    │   └── requirements.txt
    └── Readme.md

### Step 2

Setup the Env files. for more info read the indivisual readme.md from each services

### Step 3

1) Run RDS Service ` ~/rndenrichmentmicroservices/pd_rds$docker-compose up --build`
2) Run Mino Service ` ~/rndenrichmentmicroservices/pd_minio$docker-compose up --build`
3) Run VSE Service ` ~/rndenrichmentmicroservices/pd_vse$docker-compose up --build`
4) Run Frame Service ` ~/rndenrichmentmicroservices/pd_frames$docker-compose up --build`
5) Run Detectron Service ` ~/rndenrichmentmicroservices/pd_detectron2$docker-compose up --build`
6) Run OCR Service ` ~/rndenrichmentmicroservices/pd_ocr$docker-compose up --build`


# Step 4

Read the indivisual Readme.md from the folders

