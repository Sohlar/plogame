#!/bin/bash
cd ../ai

ARCH=$(uname -m)

if [ "$ARCH" = "x86_64" ]; then
    BASE_IMAGE="nvidia/cuda:12.1.1-base-ubuntu22.04"
    REQUIREMENTS="requirements_cuda.txt"
elif [ "$ARCH" = "arm64" ]; then
    BASE_IMAGE="ubuntu:22.04"
    REQUIREMENTS="requirements_cpu.txt"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

# Ensure Docker is logged in
if ! docker info >/dev/null 2>&1; then
    echo "Docker is not running or you don't have permission to use it."
    echo "Please start Docker and ensure you have the necessary permissions."
    exit 1
fi

# Pull the base image first
docker pull "$BASE_IMAGE"

docker build -t pybase . -f ./Dockerfile \
    --build-arg BASE_IMAGE=$BASE_IMAGE \
    --build-arg REQUIREMENTS=$REQUIREMENTS \
    --no-cache

cd ../scripts
