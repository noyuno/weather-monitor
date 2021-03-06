# お天気モニタ

![image](https://raw.githubusercontent.com/noyuno/weather-monitor/master/image.jpg)

## 1. 要件

1. Raspberry Pi Zero
2. ビット・トレード・ワン ゼロワン 電子ペーパモニタ拡張基板 ADRSZEI
3. Raspbian Stretch

## 2. 仕様

1. インターネットでお天気・天気予報を取得して表示する
2. 路面凍結するかどうかを判断して表示

## 3. BalenaEtcher で書き込み

## 4. 設定

### ユーザ作成

~~~
sudo adduser noyuno
sudo usermod -aG adm,dialout,cdrom,sudo,audio,video,plugdev,games,users,input,netdev,gpio,i2c,spi noyuno
~~~
### raspi-config

- `2. Network Options/N1 Hostname`
- `2. Network Options/Wi-fi`
- `4. Localization Option/I1 Change Locale`
- `4. Localization Option/I1 Change Wi-fi Country`
- `5. Interfacing Options/P2 SSH`
- `5. Interfacing Options/P4 SPI`
- `7. Advanced Options/A1 Expand Filesystem...`

## 5. 必要なソフトのインストール

~~~
sudo apt update
sudo apt -y upgrade
sudo apt install -y python3-pip git python3-numpy python-pil fonts-noto-cjk
sudo pip3 install spidev pigpio
sudo pip3 install -r requirements.txt
git clone https://github.com/noyuno/weather-monitor
git clone https://github.com/waveshare/e-Paper
cd e-Paper/RaspberryPi\&JetsonNano/python
sudo pip3 setup.py install
~~~

## 6. サンプルスクリプトを実行

~~~
cd ~/e-Paper/RaspberryPi\&JetsonNano/python/example
python3 epd_2in13_V2_test.py
~~~

## 7. お天気スクリプトを実行

~~~
pip3 install -r requirements.txt
cp .env.example .env
nano .env
python3 run.py
...
^C
~~~

## 8. Systemctl に登録

~~~
sudo cp weather-monitor.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl start weather-monitor
sudo systemctl status $_
journalctl -xefu weather-monitor
~~~

## 9. notifydでサーバ死活監視

~~~
curl -sSL https://get.docker.com | sh
sudo apt -y install docker-compose pass gnupg2
docker login
docker-compose up
~~~
