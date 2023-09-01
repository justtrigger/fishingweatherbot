apt update $$ apt install -y python3 python3-pip
pip install -r requirements.txt
mkdir /usr/share/fishingweatherbot
cp main.py /usr/share/fishingweatherbot
cp fishingweatherbot.service /etc/systemd/system/
systemctl enable --now fishingweatherbot