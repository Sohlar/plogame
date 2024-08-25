#!/bin/bash
cd ../ai
docker build -t pybase . -f ./Dockerfile --no-cache
cd ../scripts