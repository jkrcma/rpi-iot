import argparse
import time

from aiohttp import web

from dht11 import DHT11
from RPi import GPIO


async def metrics(request):
    dht11 = DHT11(pin=request.app['gpio_pin'])

    retries = 0
    while True:
        result = dht11.read()
        if result.is_valid():
            break

        if retries > 3:
            raise web.HTTPServiceUnavailable()
        retries += 1
        time.sleep(2)

    sensor_name = request.app['sensor_name']
    out = list()
    out.append(f"# TYPE sensor_temp_celsius gauge")
    out.append(f"sensor_temp_celsius{{sensor=\"{sensor_name}\"}} {result.temperature}")
    out.append(f"# TYPE sensor_humidity_percent gauge")
    out.append(f"sensor_humidity_percent{{sensor=\"{sensor_name}\"}} {result.humidity}")
    return web.Response(text='\n'.join(out))


async def on_startup(app):
    GPIO.setmode(GPIO.BCM)


async def on_shutdown(app):
    GPIO.cleanup()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Exports temperature reading from DHT11 sensor connected over GPIO",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-g', '--gpio-pin', type=int, default=17, help="GPIO BCM number to read data from")
    parser.add_argument('-n', '--sensor-name', default='indoor', help="sensor name used in generated metrics names")
    parser.add_argument('-p', '--port', type=int, default=9190, help="/metrics endpoint port")

    args = parser.parse_args()

    app = web.Application()
    app.add_routes([web.get('/metrics', metrics)])

    app['gpio_pin'] = args.gpio_pin
    app['sensor_name'] = args.sensor_name

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, port=args.port)
