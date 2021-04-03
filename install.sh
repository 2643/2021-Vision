#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  echo "$EUID"
  exit 1
fi

apt-get install vim ffmpeg python3 python3-pip libatlas-base-dev
pip3 install opencv-python pynetworktables imutils

chmod a+x ./setup.sh
./setup.sh
