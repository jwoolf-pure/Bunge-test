#!/bin/bash
# Name of the application
NAME="Pure Exporter"
# django project directory
PROJECTDIR=/opt/pure-export
# we will communicte using this unix socketpu
# the user to run as
USER=appaccount
# the group to run as
GROUP=appaccount
# how many worker processes should Gunicorn spawn
NUM_WORKERS=8
echo "Starting $NAME as `whoami`"
# Activate the virtual environment
cd $PROJECTDIR
source ./venv/bin/activate
# Start your Exporter

exec ./venv/bin/gunicorn pure_exporter:app \
--name $NAME \
--bind=0.0.0.0:9491 \
--user=$USER \
--group=$GROUP \
--workers=$NUM_WORKERS \
--access-logfile=- \
--error-logfile=- \
--daemon