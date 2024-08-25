#!/bin/bash
cd ../ai
docker build -t plo_trainer . -f ../ai/Dockerfile.train --no-cache
cd ../scripts