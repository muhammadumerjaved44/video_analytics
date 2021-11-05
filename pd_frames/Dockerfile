FROM continuumio/miniconda3

# activate conda enviorment
RUN /bin/sh -c conda activate base


RUN apt-get update -y

RUN pip install --upgrade pip

# gcc compiler and opencv prerequisites
RUN apt-get -y install nano git build-essential libglib2.0-0 libsm6 libxext6 libxrender-dev sudo cmake ninja-build ffmpeg
RUN apt-get update && apt-get install -y python3-opencv


WORKDIR /code
COPY requirements.txt .

RUN pip install -r requirements.txt