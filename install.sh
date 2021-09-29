#!/bin/bash

# The install script needed to set up your Raspeberry Pi 4B to run Draculog

apt-get update

#apt-get upgrade

# Clang install
apt-get install clang-11 --install-suggests 

# GCC install
apt-get install build-essential manpages-dev

# Python3 install (along with part DHT install)
apt-get install python3-dev python3-pip python3-libgpiod

# Python3 DHT22 Tools
python3 -m pip install --upgrade pip setuptools wheel testresources gpiozero

pip3 install adafruit-circuitpython-dht adafruit-circuitpython-lis3dh

# Python PyRAPL Tools and permissions
pip install pyRAPL pymongo pandas


chmod -R a+r /sys/class/powercap/intel-rapl
