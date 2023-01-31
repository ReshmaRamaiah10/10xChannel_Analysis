FROM --platform=linux/amd64 ubuntu:23.04
MAINTAINER reshma9352@gmail.com

#~~~~~~~~~~~~~~
# Install Preliminaries
#~~~~~~~~~~~~~~

RUN apt-get -qq update && apt-get -qq -y install --no-install-recommends \
    automake \
    build-essential \
    curl \
    g++ \
    gcc \
    git \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    libbz2-dev \
    make \
    wget \
    zlib1g-dev 


#~~~~~~~~~~~
# Environmental Variables 
#~~~~~~~~~~~
ENV SRC /usr/local/src
ENV BIN /usr/local/bin

#~~~~~~~~~~~~~~~~~~~~~~~~
# Python from source
#~~~~~~~~~~~~~~~~~~~~~~~~
# adjust working directory 
WORKDIR $SRC

# Download 
RUN wget --no-check-certificate https://www.python.org/ftp/python/3.9.15/Python-3.9.15.tgz
RUN tar -xf Python-3.9.15.tgz

# install
RUN cd Python-3.9.15 && \
    ./configure --enable-optimizations && \
    make && \
    make altinstall
RUN python3.9 -m pip install --upgrade pip

# Set link so you can type python instead of python3.9, also make default python
RUN ln -sf /usr/local/bin/python3.9 /usr/bin/python

# install necessary packages
RUN pip install requests beautifulsoup4 python-dotenv
RUN pip install scanpy
RUN pip install leidenalg

# add the file to the docker image
COPY 10x_script.py /usr/local/src
CMD [ "python"]
WORKDIR $SRC
