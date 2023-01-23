#!/bin/bash
apt update
cd home/ubuntu
apt install python3-pip -y
apt install python3-venv -y
apt install awscli -y
apt install nginx -y

git clone https://github.com/dvdg6566/codebreaker-contest-manager
cd codebreaker-contest-manager

python3 -m venv virtualenv
source virtualenv/bin/activate
pip3 install -r requirements.txt

aws configure set region ap-southeast-1
# TODO: MAKE THIS FOR USER ONLY

touch password.py
echo 'FLASK_SECRET_KEY = "PLACEHOLDER"' >> password.py

# do this stuff
# https://medium.com/techfront/step-by-step-visual-guide-on-deploying-a-flask-application-on-aws-ec2-8e3e8b82c4f7
{
	echo '[Unit]'
	echo 'Description=Gunicorn instance for a codebreaker'
	echo 'After=network.target'
	echo '[Service]'
	echo 'User=ubuntu'
	echo 'Group=www-data'
	echo 'WorkingDirectory=/home/ubuntu/codebreaker-contest-manager'
	echo 'ExecStart=/home/ubuntu/codebreaker-contest-manager/virtualenv/bin/gunicorn -b localhost:8000 app:app'
	echo 'Restart=always'
	echo '[Install]'
	echo 'WantedBy=multi-user.target'
} >> /etc/systemd/system/codebreaker.service

systemctl start codebreaker
systemctl enable codebreaker
systemctl start nginx
systemctl enable nginx

{
	echo 'server {'
	echo 'listen 80 default_server;'
	echo 'listen [::]:80 default_server;'
	echo 'server_name codebreaker;'
	echo 'location / {'
	echo '    proxy_pass http://127.0.0.1:8000;'
	echo '    include proxy_params;'
	echo '}'
} >> /etc/nginx/sites-available/default 

systemctl restart nginx
