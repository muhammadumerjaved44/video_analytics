FROM continuumio/miniconda3

# activate conda enviorment
RUN /bin/sh -c conda activate base


RUN apt-get update -y

RUN pip install --upgrade pip

# gcc compiler and opencv prerequisites
RUN apt-get update -y && apt-get -y install \
    curl \
    nano \
    git \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    sudo \
    cmake \
    ninja-build \
    ffmpeg \
    python3-opencv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# mssql docker install
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

WORKDIR /code
COPY requirements.txt .

RUN pip install -r requirements.txt