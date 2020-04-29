# requirements: swfextract (swftools), rtmpdump, mplayer, irsend(lirc)

import argparse
import asyncio
import base64
import logging
import os
import queue
import signal
import subprocess
import sys
import threading
import time
import traceback
import urllib.parse
import xml.etree.ElementTree as et
from datetime import datetime

import requests

import dotenv
dotenv.load_dotenv('.env')

import monitor
import util
import weather

def initlogger(name, logdir):
    logdir = f'/logs' if os.environ.get('DEBUG') else f'logs'
    os.makedirs(logdir, exist_ok=True)
    starttime = datetime.now().strftime('%Y%m%d-%H%M')
    logging.getLogger().setLevel(logging.WARNING)
    logger = logging.getLogger('notifyd')
    if os.environ.get('DEBUG'):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logFormatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s',
                                     datefmt='%Y%m%d-%H%M')
    fileHandler = logging.FileHandler('{}/{}'.format(logdir, starttime))
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    return logger, starttime
    
class Main():
  def __init__(self, logger, datadir):
    self.logger = logger
    self.weather = weather.Weather(self.logger, os.environ['OWM_API_KEY'], 'default',
      os.environ['LAT'], os.environ['LON'], os.environ['KISHODAI'], os.environ['CITY'], datadir)
    self.monitor = monitor.Monitor(self.logger, self.weather, os.environ.get('DARK') is not None, datadir)
    self.weather.update()
    self.monitor.clear()

  def close(self):
    pass

  def run(self):
    while True:
      self.weather.update()
      self.monitor.update()
      time.sleep(1800)

main = None

def termed(signum, frame):
  print("shutting down...")
  if main != None:
      main.close()
  sys.exit(0)

if __name__ == "__main__":
  # log
  name = 'weather-monitor'
  datadir = f'/data' if os.environ.get('DEBUG') else f'data'
  logdir = f'/logs' if os.environ.get('DEBUG') else f'logs'
  os.makedirs(datadir, exist_ok=True)
  os.makedirs(logdir, exist_ok=True)
  logger, starttime = initlogger(name, logdir)
  logger.info(f'started {name} at {starttime}')

  # env
  envse = ['NOTIFYD_TOKEN', 'OWM_API_KEY', 'LAT', 'LON', 'KISHODAI', 'CITY']
  envsc = []
  f = util.environ(envse, 'error', False)
  util.environ(envsc, 'warning', False)
  if f:
    logger.error('error: some environment variables are not set. exiting.')
    sys.exit(1)

  # signal
  signal.signal(signal.SIGTERM, termed)

  # main
  main = Main(logger, datadir)
  main.run()
