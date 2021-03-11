#!/bin/bash

echo "Build docker image for twampy"
docker build -t twamp --file ./Dockerfile .