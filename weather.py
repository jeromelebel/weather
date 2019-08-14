#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import aiohttp
import asyncio
import datetime
import ephem
import json
import logging
import pprint
import time
import traceback

import meteo_france_weather
import orange_weather

logger = logging.getLogger("Weather")

async def get_insee_code(zip_code = None):
  if zip_code == None:
    logger.error("No zip code")
    return None
  async with aiohttp.ClientSession() as session:
    url = 'https://api-adresse.data.gouv.fr/search/?q=postcode=' + str(zip_code)
    async with session.get(url, allow_redirects = False) as resp:
      if resp.status != 200:
        logger.warning("URL: {} Error: {}".format(url, resp.status))
        return None
      my_json = await resp.text()
  try:
    data = json.loads(str(my_json))
    for feature in data["features"]:
      if "properties" in feature:
        return feature["properties"]["citycode"]
  except:
    logger.exception("Error to get insee code {}".format(sys.exc_info()[0]))
  return None

async def get_rain_with_insee_code(insee_code = None):
  global logger
  if insee_code is None:
    logger.error("No insee code")
    return None
  result = await meteo_france_weather.get_rain_with_insee_code(insee_code)
  if result is None:
    result = await orange_weather.get_rain_with_insee_code(insee_code)
  return result

async def get_rain_with_zip_code(zip_code = None):
  global logger
  if zip_code == None:
    logger.error("No zip code")
    return None
  insee_code = await get_insee_code(zip_code)
  return await get_rain_with_insee_code(insee_code)

def sunset_time(gps = None, day = None):
  if gps == None:
    logger.error("No GPS")
    return None
  if day == None:
    day = datetime.date.today()
  return calculate_time(gps, day, False)

def sunrise_time(gps = None, day = None):
  if gps == None:
    logger.error("No GPS")
    return None
  if day == None:
    day = datetime.date.today()
  return calculate_time(gps, day, True)

def next_sunset_time(gps = None):
  if gps == None:
    logger.error("No GPS")
    return None
  today_sunset = sunset_time()
  if (today_sunset - datetime.datetime.now()).total_seconds() < 0:
    today_sunset = sunset_time(gps, datetime.date.today() + datetime.timedelta(days = 1))
  return today_sunset

def next_sunrise_time(gps = None):
  if gps == None:
    logger.error("No GPS")
    return None
  today_sunrise = sunrise_time()
  if (today_sunrise - datetime.datetime.now()).total_seconds() < 0:
    today_sunrise = sunrise_time(gps, datetime.date.today() + datetime.timedelta(days = 1))
  return today_sunrise

def calculate_time(gps, day, is_rise):
  if gps == None:
    logger.error("No GPS")
    return None
  utc_time = time.daylight - (time.timezone/3600)
  o = ephem.Observer()
  o.lat, o.long, o.date = str(gps["lat"]), str(gps["lon"]), day
  sun = ephem.Sun(o)
  next_event = o.next_rising if is_rise else o.next_setting
  return ephem.Date(next_event(sun, start=o.date) + utc_time*ephem.hour).datetime()

async def debug():
  print("==> Insee:")
  insee_code = await get_insee_code(75001)
  pprint.pprint(insee_code)
  print("==> Rain for 75001:")
  result = await get_rain_with_zip_code(75001)
  pprint.pprint(result)
  print("==> Rain for wrong insee code:")
  result = await get_rain_with_insee_code(12345678)
  pprint.pprint(result)
  gps = { "lat": 48.853, "lon": 2.35 }
  print("==> Next sunset in Paris")
  result = sunset_time(gps)
  pprint.pprint(result)
  print("==> Next sunrise in Paris")
  result = sunrise_time(gps)
  pprint.pprint(result)
  print("==> insee None")
  result = await get_rain_with_zip_code(None)
  pprint.pprint(result)

if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.run_until_complete(debug())
