#!/bin/bash
cd /home/pi/homeController
git pull
pkill python
python3 main2.py