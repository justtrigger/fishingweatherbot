mkdir /usr/fishingweatherbot
cp main.py /usr/fishingweatherbot
cp fishingweatherbot.service /etc/systemd/system/
systemctl enable --now fishingweatherbot