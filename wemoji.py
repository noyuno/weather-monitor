import sys

thunderstorm_rain = '☔'
thunderstorm = "⚡"    # Code: 200's, 900, 901, 902, 905
drizzle = "💧"         # Code: 300's
rain = "🌂"            # Code: 500's
snowflake = "❄"       # Code: 600's snowflake
snowman = "☃"         # Code: 600's snowman, 903, 906
squall = '☔'
tornado = '🌀'
atmosphere = "🌁"      # Code: 700's foogy
clearSky = "☀"        # Code: 800 clear sky
fewClouds = "⛅"       # Code: 801 sun behind clouds
clouds = "☁"          # Code: 802-803-804 clouds general
hot = "🔥"             # Code: 904
defaultEmoji = "🌀"    # default emojis

def weather(s):
  if type(s) == list or type(s) == tuple:
    r = []
    for t in s:
      r.append(_weather(t))
    return ''.join(r)
  else:
    return _weather(s)

def _weather(s):
  id = int(s)
  s = str(s)
  if id >= 200 and id <= 202:
    return thunderstorm_rain
  elif s[0] == '2':
    return thunderstorm
  elif s[0] == '3':
    return drizzle
  elif (id >= 502 and id <= 504) or id == 511:
    return squall
  elif s[0] == '5':
    return rain
  elif id == 602 or id == 622:
    return snowman
  elif s[0] == '6':
    return snowflake
  elif id == 771:
    return squall
  elif id == 781:
    return 
  elif s[0] == '7':
    return atmosphere
  elif id >= 800 and id <= 801:
    return clearSky
  elif id >= 802 and id <= 803:
    return fewClouds
  elif id == 804:
    return clouds
  else:
    return '?'

def deg(s):
  max = 360
  unit = 8
  d = int((s + max / unit / 2- ((s + max / unit / 2) % (max / unit))) / max / unit)
  symbols = ['↓', '↙', '←', '↖', '↑', '↗', '→', '↘', '↓']
  return symbols[d]
