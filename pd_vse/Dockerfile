FROM continuumio/miniconda3

RUN apt-get update -q -y && \
    apt-get install -q -y --no-install-recommends \
        build-essential \
        manpages-dev \
        gnupg2 \
        curl \
        procps \
        subversion \
        wget \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# activate conda enviorment
RUN /bin/sh -c conda activate base

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