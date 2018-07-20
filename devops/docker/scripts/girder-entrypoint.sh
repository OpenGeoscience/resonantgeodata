#!/bin/bash

GIRDER_START="girder serve"

# Start girder as a daemon
($GIRDER_START > entrypoint.log 2>&1) &

# Wait for it to be done starting
until grep -qi 'engine bus started' entrypoint.log; do sleep 1; done;

# Provision girder instance
python /resonantgeodata/devops/docker/scripts/bootstrap-girder.py

# Tear down Girder
kill $(pgrep -f girder)

$GIRDER_START
