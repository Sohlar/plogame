#!/bin/bash
cd ../ai

ARCH=$(uname -m)

if [ "$ARCH" = "x86_64" ]; then
    REQUIREMENTS="requirements_cuda.txt"
elif [ "$ARCH" = "arm64" ]; then
    REQUIREMENTS="requirements_cpu.txt"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

docker build -t pybase . -f ./Dockerfile --build-arg REQUIREMENTS=$REQUIREMENTS --no-cache

cd ../scripts
