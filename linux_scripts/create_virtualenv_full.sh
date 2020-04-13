#!/bin/bash
sudo apt update
sudo apt install python3.7
sudo apt install python3-pip
sudo pip3 install virtualenv
sudo python3 -m virtualenv ../venv
source ../venv/bin/activate
sudo python3 --version
sudo which python3
deactivate