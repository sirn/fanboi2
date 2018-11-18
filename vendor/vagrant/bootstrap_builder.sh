#!/bin/sh
set -xe

apt-get update
apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        dirmngr \
        gnupg2 \
        software-properties-common

#
# Docker
#

curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
apt-get update
apt-get install -y docker-ce docker-compose

systemctl enable docker
systemctl start docker
usermod -aG docker vagrant

#
# IMG
#

apt-get update
apt-get install -y libseccomp-dev uidmap
echo 1 > /proc/sys/kernel/unprivileged_userns_clone

_img_sha256="6b7b660fa0a4c4ab10aa2c2d7d586afdbc70cb33644995b0ee0e7f77ddcc2565"
_img_version="v0.5.4"
curl -fSL "https://github.com/genuinetools/img/releases/download/$_img_version/img-linux-amd64" -o "/usr/local/bin/img" \
    && echo "${_img_sha256}  /usr/local/bin/img" | sha256sum -c - \
    && chmod a+x "/usr/local/bin/img"

#
# Google Cloud SDK
#

curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
apt-add-repository "deb [arch=amd64] http://packages.cloud.google.com/apt cloud-sdk-$(lsb_release -c -s) main"
apt-get update
apt-get install -y google-cloud-sdk
