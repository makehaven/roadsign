FROM ubuntu:trusty

RUN apt-get update -qq && apt-get install -y --force-yes \
    libpq-dev \
    curl \
    git \
    g++ \
    autoconf \
    automake \
    mercurial \
    libopencv-dev \
    build-essential \
    checkinstall \
    cmake \
    pkg-config \
    yasm \
    libtiff4-dev \
    libpng-dev \
    libjpeg-dev \
    libjasper-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libgtk2.0-dev \
    wget \
    libtool \
    python3-pip

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip3 install pip --upgrade
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app