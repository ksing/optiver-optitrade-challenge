#!/bin/bash

sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get -y update
sudo apt-get -y install python3.6
sudo ln -sf /usr/bin/python3.6 /usr/bin/python3
sudo python3.6 -m pip install -U pip
sudo apt-get -y autoremove
