#!/usr/bin/python
# -*- coding:utf-8 -*-
import base64
import io
import json
import logging
import os
import sys
import time
import traceback
from datetime import datetime

import requests
import emoji

import wemoji
from PIL import Image, ImageDraw, ImageFont

if not os.environ.get('DEBUG'):
  from waveshare_epd import epd2in13_V2

def ctemp(atemp):
  return int(float(atemp) - 273.15)

class Monitor():
  def __init__(self, logger, weather):
    self.logger = logger
    self.weather = weather
    self.width = 250
    self.height = 122
    self.enable_epd = os.environ.get('DEBUG') is None
    if self.enable_epd:
      self.epd = epd2in13_V2.EPD()
    self.font_size = [8, 10, 13, 17, 22, 28, 35, 43]
    self.fonts = {
      'japanese': {},
      'emoji': {},
    }
    self.font_file_dirs = [
      '/usr/share/fonts/noto',
      '/usr/share/fonts/opentype/noto'
    ]
    self.font_file_names = {
      'japanese': 'NotoSansCJK-Regular.ttc',
      'emoji': 'NotoEmoji-Regular.ttf'
    }
    self.font_files = {}
    for (name, filename) in self.font_file_names.items():
      for dir in self.font_file_dirs:
        if os.path.exists(f'{dir}/{filename}'):
          self.font_files[name] = f'{dir}/{filename}'
          break
    # check
    for name in self.font_file_names.keys():
      if not self.font_files.get(name):
        raise Exception(f'font file not found: {name}')

    missing = list(filter(lambda n: not self.font_files.get(n), self.font_file_names))
    if len(missing) > 0:
      raise Exception('font file not found: {%s}' % ([self.font_file_names[m] for m in missing]))

    for s in self.font_size:
      self.fonts['japanese'][s] = ImageFont.truetype(font_file, s)
      self.fonts['emoji'][s] = ImageFont.truetype(emoji_file, s)
    self.imagefile = '/data/image.png'

  def clear(self):
    if self.enable_epd:
      self.epd.init(self.epd.FULL_UPDATE)
      self.epd.Clear(0x00)
    else:
      im = Image.new('1', (self.width, self.height))
      im.save(self.imagefile)

  def textsize(self, text, size):
    ret = []
    for c in str(text):
      d = None
      if c in emoji.UNICODE_EMOJI:
        d = self.draw.textsize(c, font=self.fonts['emoji'][size])
      else:
        d = self.draw.textsize(c, font=self.fonts['japanese'][size])
      ret.append(d)
    return ret

  def drawText(self, x, y, text, **option):
    size = 10 if option.get('size') is None else option['size']
    ts = self.textsize(str(text), size)
    if option.get('align'):
      div = 1 if option['align'] == 'right' else 2
      x -= sum([d[0] for d in ts]) / div

    n = 0
    for c in str(text):
      f = 'emoji' if c in emoji.UNICODE_EMOJI else 'japanese'
      self.draw.text((x, y - ts[n][1]), c, font=self.fonts[f][size], fill = 0)
      x += ts[n][0]
      n += 1
    return ts

  def draw_main_current(self):
    now = datetime.now()
    stime = '%m/%d %H:%M'
    date = 'N' + now.strftime(stime)
    if self.weather.last_update is not None:
      date += ' U' + self.weather.last_update.strftime(stime)
    if self.logger.level == logging.DEBUG:
      date += ' D'
    self.drawText(self.width - 3, 13, date, align='right')
    
    yoffset = 12
    xoffset = 10
    self.drawText(25 + xoffset, 10 + yoffset, self.weather.city, align='center', size=13)
    f = self.weather.owm['current']
    self.drawText(25 + xoffset, 23 + yoffset, '現在の天気', align='center', size=13)
    self.drawText(25 + xoffset, 65 + yoffset, wemoji.weather(list(map(lambda s: s['id'], f['weather']))), size=43, align='center')
    # w = self.weather.today if now.hour < 12 else self.weather.tomorrow
    # self.drawText(20, 40, 20, w.weather)
    self.drawText(13 + xoffset, 80 + yoffset, '%s%d%s' % ('', ctemp(f['feels_like']), 'C'), align='center')
    self.drawText(37 + xoffset, 80 + yoffset, '%s%d%s' % ('', int(f['humidity']), '%'), align='center')
    if f.get('rain'):
      self.drawText(13 + xoffset, 90 + yoffset, '%s%d%s' % ('☔', int(f['rain']), 'mm'), align='center')
    if f.get('snow'):
      self.drawText(37 + xoffset, 90 + yoffset, '%s%d%s' % ('❄', int(f['snow']), 'cm'), align='center')
    if f['wind_speed'] != 0:
      self.drawText(13 + xoffset, 100 + yoffset, wemoji.deg(f['wind_deg']), align='center')
      self.drawText(37 + xoffset, 100 + yoffset, '%s%d%s' % ('', int(f['wind_speed']), 'm'), align='center')



  def draw_main_hourly(self):
    xinit = 80
    x = xinit
    width = 30
    height = 550 # dummy (55)
    y = 30
    span = 3
    count = 0
    for f in self.weather.owm['hourly']:
      if f['dt'] < self.weather.owm['current']['dt']:
        continue
      count += 1
      if count % span != 0:
        continue
      self.drawText(x, y + 0, datetime.fromtimestamp(f['dt']).strftime('%H'), align='center')
      self.drawText(x, y + 25, wemoji.weather(list(map(lambda s: s['id'], f['weather']))), size=22, align='center')
      self.drawText(x, y + 35, '%s%d%s' % ('', ctemp(f['feels_like']), 'C'), align='center')
      if f.get('snow'):
        self.drawText(x, y + 45, '%s%d%s' % ('❄', int(f['snow']), 'cm'), align='center')
      elif f.get('rain'):
        self.drawText(x, y + 45, '%s%d%s' % ('☔', int(f['rain']), 'mm'), align='center')

      x += width
      if x + width / 2 > self.width:
        y += height
        x = xinit

  def draw_main_keiho(self):
    xinit = 70
    yinit = 90
    x = 0
    y = 0
    keiho2 = False
    text = ' '.join(self.weather.keiho)
    for c in text:
      if xinit + x + 13 > self.width:
        y += 13
        keiho2 = True
      ts = self.drawText(xinit + x, yinit + y, c, size=13)
      x += ts[0][0]

    if not keiho2 and self.weather.keikai:
      self.drawText(xinit, yinit + 13, ' '.join(self.weather.keikai), size=13)



  def emoji_test(self):
    emoji = u'☔⚡💧🌂❄⛄☔🌀🌁☀⛅☁🔥🌀'
    y = 0
    for f in self.fonts.keys():
      self.drawText(3, 3 + y, f)
      x = 0
      for e in emoji:
        self.drawText(50 + x, 3 + y, e, font=f)
        x += 10
      y += 20

  def update(self):
    try:
      image = Image.new('1', (self.width, self.height), 255)
      self.draw = ImageDraw.Draw(image)
      #self.emoji_test()
      self.draw_main_current()
      self.draw_main_hourly()
      self.draw_main_keiho()

      if self.enable_epd:
        epd.displayPartial(epd.getbuffer(image))

      # debug
      image.save(self.imagefile)
      
      buffered = io.BytesIO()
      image.save(buffered, format='PNG')
      image_byte = buffered.getvalue()
      image_b64 = base64.b64encode(image_byte)
      image_b64s = image_b64.decode('utf-8')

      # url = 'http://notifyd:5050' if os.environ.get('DEBUG') else 'localhost:5050'
      # requests.post(url, json={
      #   'token': os.environ.get('NOTIFYD_TOKEN'),
      #   'imagefile': image_b64s
      # })

    except Exception as ex:
      self.logger.exception(ex)
