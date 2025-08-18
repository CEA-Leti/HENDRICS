# Copyright (C) 2025 CEA - All Rights Reserved
# 
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

# Docker image for Buildroot compilation environment based on Ubuntu 22.04.
FROM ubuntu:22.04
WORKDIR /home/eEDR_testbed
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies required for scripts execution
RUN apt-get update && apt-get install -y git \
    make \
    cmake \
    libtool \
    autoconf \
    sudo \
    wget \
    fdisk \
    kmod

# Install dependencies required for Buildroot compilation
RUN apt-get install -y sed \
    binutils \
    diffutils \
    findutils \
    build-essential \
    gcc \
    g++ \ 
    bash \
    patch \
    gzip \
    bzip2 \
    unzip \
    perl \
    tar \
    cpio \
    rsync \
    file \
    bc

