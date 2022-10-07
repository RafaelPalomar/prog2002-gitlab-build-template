#!/bin/bash

# We build from the parent dir in order to copy it
cd ..

# Remove the old container
docker rm -f build-template

# Build container
docker build --build-arg cores=1 -f Docker/Dockerfile -t build-template .

# Start container
docker run -it -d --name build-template build-template /bin/sh
