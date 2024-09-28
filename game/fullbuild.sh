#!/bin/bash
cd ../scripts
./build_base_image.sh

cd ../game
docker build -t plo . -f Dockerfile --no-cache
