from random import randint
from time import time, sleep

from blinkt import set_pixel, show
from dht11 import DHT11
from RPi import GPIO

phase_schema = [0.02, 0.05, 0.1, 0.2, 0.3, 0.2, 0.1, 0.05, 0.02]
phase_num = 33 + 10
led_num = 8
led_color = [255, 0, 0]
temp_phases = [
    (0, 0, 255),
    (0, 127, 255),
    (0, 255, 127),
    (0, 255, 0),
    (127, 255, 0),
    (255, 255, 0),
    (255, 127, 0),
    (255, 0, 0),
]
temp_range = (18, 30)
temp_step = (temp_range[1] - temp_range[0]) / len(temp_phases)


GPIO.setmode(GPIO.BCM)
dht11 = DHT11(pin=17)

phase_full = [0] * led_num + phase_schema + [0] * led_num
phase_len = len(phase_full)
phase_half = int(phase_num / 2)

last_check = 0
last_temp = temp_range[0]
current_color = (0, 0, 0)


def get_temperature():
    retries = 0
    while True:
        ret = dht11.read()
        if ret.is_valid():
            return ret.temperature

        if retries > 2:
            return
        retries += 1


while True: 
    if time() - last_check > 60:
        last_check = time()
        temp = get_temperature()
        print("Read new temperature: %s" % (temp))
        if temp:
            for i, temp_phase in enumerate(temp_phases):
                if temp > temp_range[0] + i * temp_step:
                    current_color = temp_phase
                    print("Found new color %s, temperature threshold: %s" % (current_color, temp_range[0] + i * temp_step))
            last_temp = temp

    for phase in range(0, phase_num):
        if phase < phase_half:
            phase_end = phase_len - phase
            phase_start = phase_end - led_num
        else:
            phase_start = phase - phase_half
            phase_end = phase_start + led_num

        for led, brightness in enumerate(phase_full[phase_start:phase_end]):
            set_pixel(led, *current_color, brightness=brightness)

        show()
        sleep(0.001 + max(0, temp_range[1] - last_temp)**2 * 0.002)
