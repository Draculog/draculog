#!/bin/bash

# The install script needed to set up your Raspeberry Pi 4B to run Draculog

apt-get update

apt-get upgrade

# Clang install
apt-get install clang-11 --install-suggests 

# GCC install
apt-get install build-essential manpages-dev

# Python3 install (along with part DHT install)
apt-get install python3-dev python3-pip python3-libgpiod

# Python3 DHT22 Tools
python3 -m pip install --upgrade pip setuptools wheel

pip3 install adafruit-circuitpython-dht

pip3 install adafruit-circuitpython-lis3dh
