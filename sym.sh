#/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  echo "$EUID"
  exit 1
fi

chmod a+x duplicate_stream.sh
ln ./split-camera.service /etc/systemd/system/
ln ./galactic_search/gs_ball_tracking.service /etc/systemd/system/
ln ./galactic_search/gs_marker_tracking.service /etc/systemd/system/
ln ./bounce_path/bounce_path_code_portion.service /etc/systemd/system/