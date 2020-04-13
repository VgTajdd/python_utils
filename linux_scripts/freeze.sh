#!/bin/bash
source ../venv/bin/activate
pip3 freeze > requirements.txt
deactivate