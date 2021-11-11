FROM continuumio/miniconda3

# activate conda enviorment
RUN /bin/sh -c conda activate base


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

RUN apt-get update -y \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && ACCEPT_EULA=Y apt-get install -y mssql-tools

RUN ln -s /opt/mssql-tools/bin/* /usr/local/bin/

RUN apt-get install -y unixodbc-dev \
    libgssapi-krb5-2


WORKDIR /code
COPY requirements.txt .

ENV CONDA_PACKAGES="-c anaconda pyodbc"

RUN conda install $CONDA_PACKAGES

RUN pip install -r requirements.txt