# checkNetService
Проверка наличия доступа в Интернет и к определенным ресурсам

sudo apt-get update
sudo apt-get install python3-dev libjpeg-dev zlib1g-dev libopenblas-dev (libatomic1)

mkdir checkService
cd checkService
python -m venv venv
source venv/bin/activate
(deactivate)

pip list
Package Version
------- -------
pip     25.1.1

pip install flask requests matplotlib apscheduler

pip list
Package            Version
------------------ -----------
APScheduler        3.11.2
blinker            1.9.0
certifi            2026.2.25
charset-normalizer 3.4.5
click              8.3.1
contourpy          1.3.3
cycler             0.12.1
Flask              3.1.3
fonttools          4.61.1
idna               3.11
itsdangerous       2.2.0
Jinja2             3.1.6
kiwisolver         1.4.9
MarkupSafe         3.0.3
matplotlib         3.10.8
numpy              2.4.2
packaging          26.0
pillow             12.1.1
pip                25.1.1
pyparsing          3.3.2
python-dateutil    2.9.0.post0
requests           2.32.5
six                1.17.0
tzlocal            5.3.1
urllib3            2.6.3
Werkzeug           3.1.6


Добавляем сервисы в systemD
Работаем от pi

Для простого испытания достаточно - python3 main.py

sudo nano /etc/systemd/system/checkService.service (python3.13?):

[Unit]
Description=checkService
After=network-online.target nss-user-lookup.target

[Service]
User=pi
Group=pi
WorkingDirectory=/home/pi/checkService
Environment="PYTHONPATH=/home/pi/checkService/venv/lib/python3.13/site-packages"
ExecStartPre=/usr/bin/sleep 10
ExecStart=/home/pi/checkService/venv/bin/python3.13 /home/pi/checkService/main.py

RestartSec=10
Restart=always
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target

Настраивам systemD:

sudo systemctl daemon-reload
sudo systemctl enable --now checkService.service
systemctl status checkService.service

Если от Пи, то права на папку менять нне нужно.
ls -l
total 4
drwx------ 13 pi pi 4096 Mar  6 12:25 pi
Если от Пи, то права на папку менять нне нужно.

/checkService $ ls -l
total 20
-rw-rw-r-- 1 pi pi  277 Mar  6 12:26 config.json
-rw-rw-r-- 1 pi pi 6471 Mar  6 12:27 main.py
drwxrwxr-x 2 pi pi 4096 Mar  6 12:24 static
drwxrwxr-x 6 pi pi 4096 Mar  6 11:57 venv
