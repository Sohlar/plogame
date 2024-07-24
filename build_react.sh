#!/bin/bash
cd frontend
npm run build
rm -rf ../poker/templates/build
rm -rf ../poker/static/static
mv build ../poker/templates/
mv ../poker/templates/build/static ../poker/static/
