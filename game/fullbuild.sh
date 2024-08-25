#!/bin/bash
cd ./pybase_image
docker build -t pybase . -f ./Backend/Dockerfile --no-cache
cd ../
docker build -t plo . -f Dockerfile --no-cache