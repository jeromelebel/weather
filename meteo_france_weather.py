#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import aiohttp
import asyncio
import codecs
import json
import logging
import pprint

logger = logging.getLogger("MeteoFranceWeather")


async def get_rain_with_gps(gps):
  global logger
  async with aiohttp.ClientSession() as session:
    url = "https://meteofrance.com/"
    async with session.get(url, allow_redirects = False) as resp:
      cookies = session.cookie_jar.filter_cookies('https://meteofrance.com')
      cookie_value = None
      for key, cookie in cookies.items():
          if key == 'mfsession':
              cookie_value = cookie.value
      if cookie_value is None:
        return None
      token = codecs.encode(cookie_value, 'rot_13')
  headers = { "Authorization": "Bearer " + token, "User-Agent": "curl/7.68.0" }
  async with aiohttp.ClientSession(headers = headers) as session:
    url = "https://rpcache-aa.meteofrance.com/internet2018client/2.0/nowcast/rain?lat={0:0.5f}&lon={1:0.5f}".format(gps["lat"], gps["lon"])
    async with session.get(url, allow_redirects = False) as resp:
      if resp.status != 200:
        logger.error("URL: {} Error: {}".format(url, resp.status))
        return None
      my_json = await resp.text()
  if my_json == "":
    logger.error("JSON empty")
    return None
  try:
    result = json.loads(my_json)
  except:
    logger.exception("Error with json: " + pprint.pformat(my_json))
    result = None
  if not "properties" in result or result["properties"] is None:
    logger.error("No properties in " + pprint.pformat(result))
    return None
  if not "forecast" in result["properties"] or result["properties"]["forecast"] is None:
    logger.error("No forecast in " + pprint.pformat(result))
    return None
  converted = []
  for element in result["properties"]["forecast"]:
    element["niveauPluie"] = element["rain_intensity"]
    element["niveauPluieText"] = element["rain_intensity_description"]
    converted.append(element)
  return converted

async def get_rain_with_insee_code(insee_code):
  global logger
  if insee_code == None:
    logger.error("No insee code")
    return None
  async with aiohttp.ClientSession() as session:
    url = "http://www.meteofrance.com/mf3-rpc-portlet/rest/pluie/{}0".format(str(insee_code))
    async with session.get(url, allow_redirects = False) as resp:
      if resp.status != 200:
        logger.error("URL: {} Error: {}".format(url, resp.status))
        return None
      my_json = await resp.text()
  if my_json == "":
    logger.error("JSON empty")
    return None
  try:
    result = json.loads(my_json)
  except:
    logger.exception("Error with json: " + pprint.pformat(my_json))
    result = None
  if not "dataCadran" in result or result["dataCadran"] is None:
    logger.error("No dataCadran in " + pprint.pformat(result))
    return None
  return result["dataCadran"]

async def main():
  print("==> GPS")
  rain = await get_rain_with_gps({ "lat": 48.83237, "lon": 2.355565 })
  pprint.pprint(rain)
  print("==> Rain for Paris")
  rain = await get_rain_with_insee_code(75101)
  pprint.pprint(rain)
  print("==> Rain for None")
  rain = await get_rain_with_insee_code(None)
  pprint.pprint(rain)

if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
