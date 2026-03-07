# checkNetService
Проверка наличия доступа в Интернет и к определенным ресурсам

![Alt text](pics/raspberry.png)

## Настройка выполнена для устройства RaspberryPi.  
- Плата: Raspberry Pi 2 Model B
- ОСистема: Raspberry Pi OS Lite (Debian)
- Архитектура: ARMv7
- ЦПУ: Broadcom BCM2836, 4 ядра ARM Cortex‑A7 @ 900 МГц
- ОЗУ: 1 ГБ LPDDR2
- Сеть: 100 Мбит/с Ethernet

## Открытые порты.
- 22 -- основной порт для администрирования
- 1500 -- веб-интерфейс сервиса 

## Установка пакетов глобально в систему.
```
sudo apt-get update
sudo apt-get install python3-dev libjpeg-dev zlib1g-dev libopenblas-dev
sudo apt-get install libatomic1 -- обычно это не нужно
```

## Создаем папку для проекта и виртуальное окружение.
```
mkdir checkService
cd checkService
python -m venv venv
source venv/bin/activate
(deactivate -- для выхода из виртуального окружения)
```

## Устанавливаем библиотеки внутри виртуального окружения.
```
pip install flask requests matplotlib apscheduler
```

Версии бибилотек:
```
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
```

## Добавляем сервис в systemD.

Работаем от пользователя pi, поэтому права на папку пользователя менять не нужно (drwx------). Создаем файл /etc/systemd/system/checkService.service

(Для простого ручного испытания достаточно - python3 main.py)

```
[Unit]
Description=checkService
After=network-online.target nss-user-lookup.target

[Service]
User=pi
Group=pi
WorkingDirectory=/home/pi/checkService
Environment="PYTHONPATH=/home/pi/checkService/venv/lib/python3.13/site-packages" --- python3.13?
ExecStartPre=/usr/bin/sleep 10
ExecStart=/home/pi/checkService/venv/bin/python3.13 /home/pi/checkService/main.py --- python3.13?

RestartSec=10
Restart=always
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

## Настраиваем systemD.
```
sudo systemctl daemon-reload
sudo systemctl enable --now checkService.service
systemctl status checkService.service
```
