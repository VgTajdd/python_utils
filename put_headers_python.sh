#!/bin/bash
source venv/bin/activate
DIR=$PWD/dir
python3 put_headers_python.py $DIR
deactivate
