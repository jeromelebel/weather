#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import aiohttp
import asyncio
import logging
import pprint
import xml.dom.minidom

logger = logging.getLogger("OrangeWeather")

def get_classes_list_for_node(node):
  if not node.hasAttribute("class"):
    return []
  string = node.getAttribute("class").strip()
  classes = string.split(" ")
  return list(filter(None, classes))

def get_class_suffix_with_classes(suffix, classes):
  for my_class in classes:
    if my_class.startswith(suffix):
      return my_class[len(suffix):]
  return None

def get_legend_from_legend_node(legend_node):
  legend = {}
  for legend_elements in legend_node.childNodes:
    if not legend_elements.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
      pass
    rain_index = get_class_suffix_with_classes("rain", get_classes_list_for_node(legend_elements))
    if rain_index is None:
      pass
    for node in legend_elements.childNodes:
      if node.nodeType == xml.dom.minidom.Node.TEXT_NODE:
        legend[rain_index] = node.data.strip()
  return legend

def get_rain_from_graf_node(graf_node, legend):
  result = []
  for node in graf_node.childNodes:
    if not node.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
      pass
    rain_index = get_class_suffix_with_classes("rain-", get_classes_list_for_node(node))
    if rain_index is None:
      pass
    pluie = { "niveauPluieText": legend[rain_index], "niveauPluie": int(rain_index) }
    result.append(pluie)
  return result
    
async def get_rain_with_insee_code(insee_code):
  global logger
  if insee_code == None:
    logger.error("No insee code")
    return None
  url = "https://meteo.orange.fr/meteo/fragments/rain/city/{}".format(str(insee_code))
  async with aiohttp.ClientSession() as session:
    async with session.get(url, allow_redirects = False) as resp:
      if resp.status != 200:
        logger.warning("URL: {} Error: {}".format(url, resp.status))
        return None
      my_data = await resp.text()
  if my_data == "":
    logger.error("Data empty {}".format(url))
    return None
  try:
    result = []
    legend = {}
    my_dom = xml.dom.minidom.parseString(my_data)
    for element in my_dom.getElementsByTagName("ol"):
      if element.hasAttribute("class") and element.getAttribute("class") == "graphique-graf-list":
        graf_list = element
      if element.hasAttribute("class") and element.getAttribute("class") == "graphique-legend-list":
        legend_list = element
    legend = get_legend_from_legend_node(legend_list)
    result = get_rain_from_graf_node(graf_list, legend)
  except:
    logger.exception("Error with xml: " + pprint.pformat(my_data))
    result = None
  return result

async def main():
  print("==> Rain for Paris")
  result = await get_rain_with_insee_code(75101)
  pprint.pprint(result)
  print("==> Rain for None")
  result = await get_rain_with_insee_code(None)
  pprint.pprint(result)

if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
