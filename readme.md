# お天気モニタ

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
sudo apt install -y python3-pip git libopenjp2-7 libtiff5 python3-numpy
sudo pip3 install pillow spidev RPi.GPIO
git clone https://github.com/noyuno/weather-monitor
~~~


## 6. エディタ等のインストール

~~~
sudo apt install -y zsh vim tmux
git clone https://github.com/noyuno/dotfiles
./dotfiles/bin/dfdeploy
~~~

## 7. サンプルスクリプトを実行

~~~
python3 adrszEI_sample_bmp.py ADRSZEI-Displey_250x128.bmp
python3 adrszEI_sample_namecard.py
~~~
