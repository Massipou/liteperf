#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

import time
from rpi_ws281x import PixelStrip, Color
import argparse
import RPi.GPIO as GPIO
import pyaudio

RATE = 44100
BUFFER = 882

p = pyaudio.PyAudio()
stream = p.open(
    format = pyaudio.paFloat32,
    channels = 1,
    rate = RATE,
    input = True,
    output = False,
    frames_per_buffer = BUFFER
)


# Configuration des broches
bouton_pin = 17

# Configuration initiale de la GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(bouton_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# LED strip configuration:
LED_COUNT = 600        # Number of LED pixels.
LED_PIN = 12         # GPIO pin connected to t6he pixels (18 uses PWM!).
#LED_PIN = 18        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

ACIDBLUE = Color(240,248,255)
REDPURP = Color(180, 0, 25)
TURQOISE = Color(0, 255, 125)
REBECCAPURPLE = Color(102, 51, 153)
DARKVIOLET = Color(125, 0, 125)
BLUEPURP = Color(10, 0, 255)
REDDORANG = Color(125, 30, 30)
MAGICRED = Color(255, 0, 20)
# Define functions which animate LEDs in various ways.

def doubleColorSlide(strip, color, color2, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    numpixel = int(round(strip.numPixels()/2, 0))
    for i in range(numpixel):
        strip.setPixelColor(i, color)
        if i%10 == 0:
            stripenumber = int(i/5)+5
        for j in range (stripenumber):
            if j%2 == 0:
                strip.setPixelColor(i-(j*5), color2)
                strip.setPixelColor(strip.numPixels() - (i-(j*5)), color2)
            else:
                strip.setPixelColor(i-(j*5), color)
                strip.setPixelColor(strip.numPixels() - (i-(j*5)), color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def colorFullSlide(strip, color, color2, iterations=20, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(iterations):
        for j in range(-5, 5, 1):
            for k in range(0, strip.numPixels() + 5, 5):
                """r = strip.numPixels() - j"""
                if k%10 < 5:
                    strip.setPixelColor((k+j), color)
                else:
                    strip.setPixelColor((k+j), color2)
                time.sleep(wait_ms/140000.0)
            strip.show()

def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(1, LED_COUNT, 3):
        strip.setPixelColor(i, color)
        strip.setPixelColor(i-1, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        while True: 
            theaterChase(strip, Color(127, 127, 127))  # White theater chase
            colorFullSlide(strip, REDPURP, DARKVIOLET)
            rainbowCycle(strip)
            print('Color wipe animations.')
            colorWipe(strip, Color(255, 0, 0))  # Red wipe
            colorWipe(strip, Color(0, 255, 0))  # Green wipe
            colorWipe(strip, Color(0, 0, 255))  # Blue wipe
            print('Theater chase animations.')
            theaterChase(strip, Color(127, 0, 0))  # Red theater chase
            theaterChase(strip, Color(0, 0, 127))  # Blue theater chase
            print('Rainbow animations.')
            rainbow(strip)
            rainbowCycle(strip)
            theaterChaseRainbow(strip)
            theaterChaseRainbow(strip)
            theaterChaseRainbow(strip)

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0), 10)

