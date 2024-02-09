#!/bin/bash -x
cd /opt 
yum install -y epel-release yum-utils 
yum-config-manager --enable powertools 
yum install -y https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-8.noarch.rpm https://mirrors.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-8.noarch.rpm 
yum install -y python3.11 ffmpeg 
python3.11 -m venv /venv 
/venv/bin/python -m pip install -r requirements.txt 
/venv/bin/python team-radio.py