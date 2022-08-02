#!/bin/bash

#pd + python libs (30 min)
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install pd -y
sudo apt-get install python3-pil -y
sudo apt-get install python3-pip -y
pip3 install --upgrade numpy==1.19.5 -y
pip3 install python-osc
pip3 install os-sys
pip3 install luma.lcd
pip3 install luma.oled

#configuration du port série
sudo chmod 666 /dev/ttyS0
sudo chmod 666 /dev/ttyAMA0

#enlever "console=serial0, 115200" dans /boot/cmdline.txt et ajouter quiet
#ajouter ça à la fin de /boot/config.txt et pas de trucs liés au bluethooth :)))
sudo sed -i 's/console=serial0,115200/ /g' /boot/cmdline.txt
echo " quiet" | sudo tee -a /boot/cmdline.txt

sudo sed -i 's/dtoverlay=vc4-kms-v3d/ /g' /boot/config.txt
echo "disable_splash=1
boot_delay=0
dtparam=i2c_arm=on
dtparam=i2s=on
dtoverlay=audioinjector-wm8731-audio" | sudo tee -a /boot/config.txt

#copie des externals pd firm V3
sudo cp /home/pi/myfiles/btn.pd /root/Pd/externals/
sudo cp /home/pi/myfiles/tgle.pd /root/Pd/externals/
sudo cp /home/pi/myfiles/multi.pd /root/Pd/externals/

#serveur apache php + nouveau path
sudo apt install apache2 -y
sudo apt install php php-mbstring -y

sudo chgrp -R www-data /home/pi/myfiles/
sudo chmod -R 2750 /home/pi/myfiles/

#lancement du systeme au démmarage (fonctionne pas encore)
echo "[Unit]
Description=Python-PD
After=triggerhappy.service
//After=rc-local.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/pi/myfiles/main_ssd1307.py
User=pi
Group=pi
Restart=always

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/python-pd.service
sudo systemctl enable python-pd.service

#ensuite setup de la carte son :

sudo reboot
