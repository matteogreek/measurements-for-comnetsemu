#!/bin/bash

echo "Build docker image for dind"
docker build -t twamp --file ./Dockerfile.dind .
docker build -t ditg --file ./Dockerfile.ditg .