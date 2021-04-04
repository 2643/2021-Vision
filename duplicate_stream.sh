#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  echo "$EUID"
  exit 1
fi

rmmod v4l2loopback
modprobe v4l2loopback video_nr=20,21,22,23,24,30
# /dev/video30 is used for 2020-vision, not in this repo nor 2020-vision.
# ffmpeg -f video4linux2 -i /dev/v4l/by-id/usb-046d_HD_Pro_Webcam_C920_4EDBE93F-video-index0 \
ffmpeg -f video4linux2 -i /dev/v4l/by-id/usb-046d_HD_Pro_Webcam_C920_5AB6901F-video-index0 \
-codec copy -f v4l2 /dev/video20 \
-codec copy -f v4l2 /dev/video21 \
-codec copy -f v4l2 /dev/video22 \
-codec copy -f v4l2 /dev/video23 \
-codec copy -f v4l2 /dev/video24