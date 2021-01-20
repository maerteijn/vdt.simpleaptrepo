FROM debian:10
MAINTAINER Martijn Jacobs <maerteijn@gmail.com>

ENV DEBIAN_FRONTEND noninteractive

# install the debian related packages for this tool + python pip
RUN apt-get update && apt-get install python3-pip gnupg dpkg-sig apt-utils --yes

# Make sure you mounted the source coude in /usr/local/src
WORKDIR /usr/local/src/