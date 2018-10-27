#!/bin/sh

apt-get update
apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg2 \
        software-properties-common

curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -

add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/debian \
    $(lsb_release -cs) \
    stable"

apt-get update
apt-get install -y \
        docker-ce \
        docker-compose

systemctl enable docker
systemctl start docker

usermod -aG docker vagrant
