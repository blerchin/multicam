#!/usr/bin/env bash

###################################
# Add this line to /etc/rc.local: #
# /home/pi/src/multicam/startup.sh > /home/pi/src/multicam/startup.log 2>&1 &
###################################

set -e

RESOLUTION=3264x2448
DELAY=120
QUALITY=90
PREFIX="/home/pi/src/multicam/images/%Y-%m-%d_%H-%M"

# if /dev/video0 is present, we can reasonably assume a webcam is plugged in
if [[ -e "/dev/video0" ]]; then
	fswebcam -r $RESOLUTION -l $DELAY --jpeg $QUALITY --no-banner -d /dev/video0 ${PREFIX}.cam1.jpg &\
	fswebcam -r $RESOLUTION -l $DELAY --jpeg $QUALITY --no-banner -d /dev/video2 ${PREFIX}.cam2.jpg &\
	fswebcam -r $RESOLUTION -l $DELAY --jpeg $QUALITY --no-banner -d /dev/video3 ${PREFIX}.cam3.jpg

else
	python3 /home/pi/src/multicam/display_images.py
fi
