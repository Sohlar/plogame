#!/bin/bash
cd ../ai
docker build -t pybase . -f ../ai/Dockerfile --no-cache
docker build -t plo_trainer . -f ../ai/Dockerfile.train --no-cache
cd ../scripts