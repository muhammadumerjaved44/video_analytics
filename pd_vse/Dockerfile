FROM continuumio/miniconda3

RUN apt-get update -q -y && \
    apt-get install -q -y --no-install-recommends \
        build-essential \
        manpages-dev \
        curl \
        procps \
        subversion \
        wget \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# activate conda enviorment
RUN /bin/sh -c conda activate base


WORKDIR /code
COPY requirements.txt .


ENV CONDA_PACKAGES="-c anaconda pyodbc"

RUN conda install $CONDA_PACKAGES

RUN pip install -r requirements.txt