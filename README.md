# weather

Python3 library to get the rain predicition from Météo France (or Orange as a backup), and gets the next sunset and sunrise date. This library methods are Async IO.

Methods:

- await weather.get_rain_with_zip_code(zip_code)

Returns the rain prediction for the zip code. The returned value is an array. Each item are for 5mn.

- await weather.get_rain_with_insee_code(insee_code)

Returns the rain prediction for the insee code. The returned value is an array. Each item are for 5mn.

- weather.get_sunset_datetime(gps, datetime = None)

Returns the sunset (as datetime) at the GPS coordinates, of day of "datetime".

- weather.get_sunrise_datetime(gps, datetime = None)

Returns the sunrise (as datetime) at the GPS coordinates, of day of "datetime".

- weather.get_next_sunset_datetime(gps)

Returns the next sunset (as datetime) at the GPS coordinates.

- weather.get_next_sunrise_datetime(gps)

Returns the next sunrise (as datetime) at the GPS coordinates.

Example:

```python
import weather

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

loop = asyncio.get_event_loop()
loop.run_until_complete(debug())
```
