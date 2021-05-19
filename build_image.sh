#!/bin/bash

echo "Build docker image for measurements and D-ITG"
docker build -t measure --file ./Dockerfile.dind .
docker build -t ditg --file ./Dockerfile.ditg .