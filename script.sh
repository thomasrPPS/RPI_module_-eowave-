sudo apt-get update
sudo apt-get upgrade

#pd + python libs (20 min)
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install pd -y
sudo apt-get install python3-pil -y
sudo apt-get install python3-pip -y
pip3 install python-osc
pip3 install os-sys
pip3 install luma.lcd
pip3 install luma.oled

#configuration du port série
sudo chmod 666 /dev/ttyS0
sudo chmod 666 /dev/ttyAMA0

#enlever "console=serial0, 115200" dans /boot/cmdline.txt et ajouter quiet
#ajouter ça à la fin de /boot/config.txt et pas de trucs liés au bluethooth :)))
sudo sed -i 's/console=serial0, 115200//g' /boot/cmdline.txt
echo "quiet" | sudo tee -a /boot/cmdline.txt

sudo sed -i 's/dtoverlay=vc4-kms-v3d//g' /boot/cmdline.txt
echo "disable_splash=1
boot_delay=0
dtparam=i2c_arm=on
dtparam=i2s=on
dtoverlay=audioinjector-wm8731-audio" | sudo tee -a /boot/config.txt

#copie des externals pd firm V3
sudo cp /home/eowave/myfiles/btn.pd /root/Pd/externals/
sudo cp /home/eowave/myfiles/tgle.pd /root/Pd/externals/
sudo cp /home/eowave/myfiles/multi.pd /root/Pd/externals/

#serveur apache php + nouveau path
sudo apt install apache2 -y
sudo apt install php php-mbstring

sudo chgrp -R www-data /home/eowave/myfiles/
sudo chmod -R 2750 /home/eowave/myfiles/

sudo sed -i 's/
<Directory /var/www>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
</Directory>
/
<Directory /home/pi/myfiles/html>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
</Directory>/g' /etc/apache2/apache2.conf


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
WantedBy=multi-user.target" | sudo tee /etc/systemd/python-pd.service
sudo systemctl enable python-pd.service

#ensuite setup de la carte son :
alsamixer -c 0
amixer -D pulse sset Master 100%

sudo reboot