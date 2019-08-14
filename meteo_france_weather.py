#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import aiohttp
import asyncio
import json
import logging
import pprint

logger = logging.getLogger("MeteoFranceWeather")

async def get_rain_with_insee_code(insee_code):
  global logger
  if insee_code == None:
    logger.error("No insee code")
    return None
  async with aiohttp.ClientSession() as session:
    url = "http://www.meteofrance.com/mf3-rpc-portlet/rest/pluie/{}0".format(str(insee_code))
    async with session.get(url, allow_redirects = False) as resp:
      if resp.status != 200:
        print("fasdas")
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
  print("==> Rain for Paris")
  rain = await get_rain_with_insee_code(75101)
  pprint.pprint(rain)
  print("==> Rain for None")
  rain = await get_rain_with_insee_code(None)
  pprint.pprint(rain)

if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
