#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  echo "$EUID"
  exit 1
fi

cd "$(dirname "$0")"

systemctl disable camera.path
systemctl disable split_camera.service
systemctl disable gs_ball_tracking.service
systemctl disable gs_marker_tracking.service
systemctl disable bounce_path_code_portion.service
systemctl disable line_detector.service

systemctl stop camera.path
systemctl stop split_camera.service
systemctl stop gs_ball_tracking.service
systemctl stop gs_marker_tracking.service
systemctl stop bounce_path_code_portion.service
systemctl stop line_detector.service