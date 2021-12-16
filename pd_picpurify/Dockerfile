FROM continuumio/miniconda3

# activate conda enviorment
RUN /bin/sh -c conda activate base


RUN apt-get update -y

RUN pip install --upgrade pip

RUN apt-get -y install curl nano git build-essential libglib2.0-0 libsm6 libxext6 libxrender-dev sudo

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

RUN pip install -r requirements.txt