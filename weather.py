import os
import sys
import threading
import xml.etree.ElementTree as et
import re
from datetime import datetime
import json

import requests

import util


class Weather():
  def __init__(self, logger, owm_apikey, name, lat, lon, kishodai, city, datadir):
    self.logger = logger
    self.name = name
    self.kishodai = kishodai
    self.city = city
    self.owm = None
    self.keiho = []
    self.keikai = []
    self.last_update = None
    self.owm_filename = f'{datadir}/{self.name}-onecall.json'
    self.owm_url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={owm_apikey}'
    self.keiho_filename = f'{datadir}/{self.name}-extra_l.xml'
    self.keiho_url = 'http://www.data.jma.go.jp/developer/xml/feed/extra_l.xml'
    self.keiho_denbun_filename = f'{datadir}/{self.name}-keiho-denbun.xml'
    self.dtformat = '%Y%m%d-%H%M'

  def update_file2(self, filename, url):
    r = requests.get(url)
    if r.status_code != 200:
      raise Exception(f'requests.get(): returned code {r.status_code}, filename={filename}, url={url}')
    f = open(filename, 'wb')
    f.write(r.content)
    f.close()
    return 0

  def update_file(self):
    last_update_file = '/data/last_update'
    if os.path.exists(last_update_file):
      self.last_update = datetime.strptime(open(last_update_file).read(), self.dtformat)
      if self.last_update.timestamp() + 60 * 30 > datetime.now().timestamp():
        self.logger.warning('update_file(): < 30 min, too quickly update, ignore')
        return

    try:
      self.update_file2(self.owm_filename, self.owm_url)
      self.update_file2(self.keiho_filename, self.keiho_url)
      self.update_file2(self.keiho_denbun_filename, self.update_file_keiho())

      f = open(last_update_file, 'w')
      self.last_update = datetime.now()
      f.write(str(self.last_update.strftime(self.dtformat)))
      f.close()
    except:
      raise

  def update_owm(self):
    f = open(self.owm_filename)
    self.owm = json.loads(f.read())
    f.close()

  def update_file_keiho(self):
    name = '気象特別警報・警報・注意報'
    ff = open(self.keiho_filename, encoding='utf-8')
    f = ff.read()
    ff.close()
    root = et.fromstring(re.sub('xmlns=".*?"', '', f, count=1))
    links = []
    for entry in root.findall(f'.//entry/title[.=\'{name}\']/../author/name[.=\'{self.kishodai}\']/../..'):
      t = datetime.strptime(entry.find('./updated').text, '%Y-%m-%dT%H:%M:%SZ')
      url = entry.find('./link').attrib['href']
      links.append((t, url))
      #print(t, entry.find('./title').text, url)

    slinks = sorted(links, key=lambda x:x[0], reverse=True)
    url = slinks[0][1]
    self.logger.debug(slinks[0][0].strftime(self.dtformat) + ' ' + url)
    return url

  def update_keiho(self):
    ff = open(self.keiho_denbun_filename, encoding='utf-8')
    f = ff.read()
    ff.close()
    f = re.sub('xmlns=".*?"', '', f)
    f = re.sub('xmlns:\\w=".*?"', '', f)
    f = re.sub('jmx_eb:', '', f)
    yoho = et.fromstring(f)

    self.keiho = []
    for t in yoho.findall(f'.//Body/Warning[@type=\'気象警報・注意報（市町村等）\']/Item/Area/Name[.=\'{self.city}\']/../../Kind'):
      n = t.find('./Name').text
      if t.find('./Status').text == '解除':
        if n in self.keiho:
          self.keiho.remove(n)
      else:
        if n not in self.keiho:
          self.keiho.append(n)

    self.logger.debug(self.keiho)


  def update(self):
    self.update_file()
    self.update_owm()
    self.update_keiho()
