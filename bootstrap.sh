#!/bin/bash
apt update
apt install python3-pip
apt install python3-venv
git clone github.com/dvdg6566/codebreaker-contest-manager
cd codebreaker-contest-manager

python3 -m venv virtualenv
source virtualenv/bin/activate

pip3 install -r requirements.txt

# sudo apt install awscli
# DO aws confgure stuff

# do this stuff
# https://medium.com/techfront/step-by-step-visual-guide-on-deploying-a-flask-application-on-aws-ec2-8e3e8b82c4f7

# sudo cp 

# sudo apt install nginx