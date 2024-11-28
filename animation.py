import time
from rpi_ws281x import PixelStrip, Color
import argparse
import threading
import math
import pyaudio
import os
import struct
import numpy as np
from scipy.fftpack import fft

# ------------ Audio Setup ---------------
# constants
CHUNK = 512 #1024             # samples per frame
FORMAT = pyaudio.paInt16     # audio format (bytes per sample?)
CHANNELS = 1                 # single channel for microphone
RATE = 44100                 # samples per second
# Signal range is -32k to 32k
# limiting amplitude to +/- 4k
AMPLITUDE_LIMIT = 4096


# ------------ LED Setup ---------------
# constants
LED_COUNT = 42        # Number of LED pixels.
# LED strip configuration:
#LED_PIN = 12         # GPIO pin connected to t6he pixels (18 uses PWM!).
LED_PIN = 18        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


# pyaudio class instance
p = pyaudio.PyAudio()

# stream object to get data from microphone
stream = p.open(
	format=FORMAT,
	channels=CHANNELS,
	rate=RATE,
	input=True,
	output=True,
	frames_per_buffer=CHUNK
)

def get_sound_data():
    # binary data
    data = stream.read(CHUNK, exception_on_overflow = False)
    # Open in numpy as a buffer
    data_np = np.frombuffer(data, dtype='h')
    # compute FFT and update line
    yf = fft(data_np)
    data = np.abs(yf[0:CHUNK])  / (512 * CHUNK)
    return(data)

def freqindex(freq):
    return round(int(freq /50))

def freq_to_color3(rseuil = -1, gseuil = 0, bseuil = 2, red = 255, green = 55, blue = 255):
    sounddata = get_sound_data() 
    bassmax = -60
    midmax = -60
    highmax = -60
    #for i in range (50, 250, 20):
    for i in range (250, 300 , 20):
        if sounddata[freqindex(i)] > bassmax : bassmax = sounddata[freqindex(i)]
    for i in range (310, 560, 20):
        if sounddata[freqindex(i)] > midmax : midmax = sounddata[freqindex(i)]
    for i in range (510, 5000, 20):
        if sounddata[freqindex(i)] > highmax : highmax = sounddata[freqindex(i)]
    if -bassmax < rseuil:
        r = int(round(((bassmax*10 + rseuil)/3)**4))
        if r < 0: r = 0
        elif r > 255: r = 255
    else: r = 0
    if -midmax < gseuil:
        g = int(round(((midmax*10 + gseuil)/3)**4))
        if g < 0: g = 0
        elif g > 255: g = 255
    else: g = 0
    if -highmax < bseuil:
        b = int(round(((highmax*10 + bseuil)/3)**4))
        if b < 0: b = 0
        elif b > 255: b = 255
    else: b = 0
    #print ("{}, {} ,{}" .format(bassmax, midmax, highmax))
    return (r, g, b)

def spectro(strip, bassr=255, bassg=20, bassb=0, highr=10, highg=0, rseuil=0, gseuil=0, bseuil=0):
    global start
    pixel_number = pixel_map.pixel_number 
    start = True
    blist = [0] * (pixel_number+2)
    j = 0
    k = 0
    while start:
        #pixel_number = pixel_map.pixel_number 
        if j > pixel_number+1: j = 0
        r, g, b = freq_to_color3(rseuil, gseuil, bseuil)
        blist[j] = b
        r =  int(round((r+g/2)/255*pixel_number))
        if r > pixel_number: r = pixel_number 
        for i in range(0, r):
            if k > pixel_number: k = 0
            if blist[j-k] >= 100: pixel_mapper(strip, pixel_number-k, highr, highg, blist[j-k])
            if blist[i-k] < 100: pixel_mapper(strip, i, bassr, bassg, bassb)
            k += 1
        for i in range(r, pixel_number):
            if k > pixel_number: k = 0 
            if blist[j-k] >= 100: pixel_mapper(strip, pixel_number-k, highr, highg, blist[j-k])
            if blist[i-k] < 100: pixel_mapper(strip, i, 0,0,0)
            k += 1
        j += 1
        strip.show()

def theaterChase(strip, r, g, b, wait_ms=50, soundreact = False):
    """Movie theater light style chaser animation.""" 
    pixel_number = int(round(LED_COUNT/pixel_map.zoom))
    for q in range(5):
        if soundreact == True: 
            r, g, b = freq_to_color3()
        for i in range(0, pixel_number - 5, 5):
            pixel_mapper(strip, i + q, r, g, b)
        strip.show()
        if not soundreact: time.sleep(wait_ms / 500.0)
        for i in range(0, pixel_number - 5, 5):
            pixel_mapper(strip, i + q, 0, 0, 0)

def sound_react_div(strip,  div):
    global start
    start = True
    pixel_number = pixel_map.pixel_number
    while start:
        for j in range (0,div,1):
            r, g, b = freq_to_color3()
            for k in range (1,pixel_number,div):
                pixel_mapper(strip, k+j, r, g, b)
            strip.show()

def sound_react_mov(strip, invert=False):
    global start
    start = True
    pixel_number = int(round(LED_COUNT/pixel_map.zoom))
    rlist = [0] * (pixel_number)
    glist = [0] * (pixel_number)
    blist = [0] * (pixel_number)
    #print (pixel_number)
    while start:
        for j in range (pixel_number):
            #rlist[j], glist[j], blist[j] = freq_to_color2()
            r, g, b = freq_to_color3()
            rlist[j] = r
            glist[j] = g
            blist[j] = b
            for k in range (pixel_number):
                if not invert: pixel_mapper(strip, k, rlist[j-k], glist[j-k], blist[j-k])
                else: pixel_mapper(strip, pixel_number-k, rlist[j-k], glist[j-k], blist[j-k])
            strip.show()

def sound_react_mov_mirror(strip, loop, invert=False,  wait_ms=50):
    global start
    start = True
    pixel_number = int(round(LED_COUNT/pixel_map.zoom))
    rlist = [0] * (pixel_number)
    glist = [0] * (pixel_number)
    blist = [0] * (pixel_number)
    middle = int(round(pixel_number/2))
    while start:
        for j in range (pixel_number, 0, -1):
            r, g, b = freq_to_color3()
            rlist[j] = r
            glist[j] = g
            blist[j] = b
            for k in range (middle+1):
                if not invert:
                    # strip.setPixelColor(k, colorlist[j-k-middle])
                    pixel_mapper(strip, k, rlist[j-k-middle],glist[j-k-middle],blist[j-k-middle])
                    # strip.setPixelColor(strip.numPixels()-k, colorlist[j-k-middle])
                    pixel_mapper(strip, pixel_number-k, rlist[j-k-middle],glist[j-k-middle],blist[j-k-middle])
                else: 
                    # strip.setPixelColor(middle + k, colorlist[j-k-middle])
                    pixel_mapper(strip, middle + k, rlist[j-k-middle],glist[j-k-middle],blist[j-k-middle])
                    # strip.setPixelColor(middle - k, colorlist[j-k-middle])
                    pixel_mapper(strip, middle - k, rlist[j-k-middle],glist[j-k-middle],blist[j-k-middle])
            strip.show()

# Create and initialize automatic thread
class theadAnimations (threading.Thread):
    def __init__(self, threadID, name, mode, stop_event):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.mode = mode
        self.start_time = time.time()
        self.stop_event = stop_event
    def run(self):
        strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        strip.begin()
        while True:
            # COCA COLA LOOP
            for cocaloop in range(3):
                while self.mode == 0:  
                    pixel_map.zoom = 1
                    updatepixelnumber()
                    pixel_map.effect = 1
                    pixel_map.effectoption = 0
                    theaterChase(strip, 127, 127, 127)
                    #spectro(strip, highr=50)           
                while self.mode == 1:
                    pixel_map.zoom = 3
                    updatepixelnumber() 
                    pixel_map.effect = 5
                    pixel_map.effectoption = 1.1
                    theaterChase(strip, 127, 0, 0, soundreact = True)
                if  self.mode == 2: 
                    pixel_map.zoom = 2
                    updatepixelnumber()
                    pixel_map.effectoption = 0
                    for i in range(2):
                        theaterChase(strip, 0, 0, 0)
                self.mode = 0
            # fourmie
            while self.mode == 0:
                print("3")
                pixel_map.zoom = 7
                pixel_map.effectoption = 1.5
                sound_react_mov(strip)
           # feu 
            while self.mode == 1:  
                pixel_map.zoom = 1
                updatepixelnumber()
                #pixel_map.miror = True
                pixel_map.effect = 3
                pixel_map.effectoption = 1.2
    #           theaterChase(strip, 127, 127, 127
                spectro(strip, highr=50)
            while self.mode == 2:  
                pixel_map.zoom = 1
                updatepixelnumber()
                pixel_map.effect = 3
                pixel_map.effectoption = 1.2
                #theaterChase(strip, 127, 127, 127
                #spectro(strip,)       
                spectro(strip, bassr=255, bassg=20, bassb=0, highr=10, highg=0, rseuil=-2, gseuil=-1, bseuil=0)
            self.mode = 0

class pixel_map:
    def init():
        pixel_map.zoom = 1
        pixel_map.gap = []

        pixel_map.rmap = [0] * (LED_COUNT + 1)
        pixel_map.gmap = [0] * (LED_COUNT + 1)
        pixel_map.bmap = [0] * (LED_COUNT + 1)

        pixel_map.effect = 1
        pixel_map.effectoption = 0
        pixel_map.gap_effect = False
        pixel_map.effect_list = []
        pixel_map.gap_effect_div = 5
        pixel_map.gap_effect_pos = 1
        pixel_map.time_wait = 1 #second
        pixel_map.last_time = time.perf_counter()
        pixel_map.last_elapsed_time = 0
        pixel_map.instruction = ""
        pixel_map.pixel_number = LED_COUNT

        pixel_map.acid = False
        pixel_map.miror = False
        pixel_map.acidposlist = [0]
        pixel_map.acidlen = 0

        i = 1
        loop = True
        #for i in range (1, pixel_map.pixel_number, 1):
        while loop == True:
            nop = int(round(math.sin(i/3) * 4 + 5)) #NUMBER OF PIXELS FOR EACH PIXELS
            pixelpos = pixel_map.acidposlist[i - 1] + nop
            if pixelpos <= pixel_map.pixel_number:
                pixel_map.acidposlist.append(pixelpos)
                #print (pixel_map.acidposlist[i])
            else:
                loop = False
                pixel_map.acidlen = len(pixel_map.acidposlist)
                print (pixel_map.acidlen)
            i = i + 1

        if pixel_map.acid: pixel_map.pixel_number = pixel_map.acidlen

pixel_map.init()

def pixel_mapper(strip, index, r, g, b):

    lol = 1.5
    acid = pixel_map.acid

    acidlist = pixel_map.acidposlist

    if not acid: pixel_map.pixel_number = int(round(LED_COUNT/pixel_map.zoom))
    else: pixel_map.pixel_number = pixel_map.acidlen

    pixels_number = pixel_map.pixel_number

    pixel_map.gap = []
    effect = pixel_map.effect

    if effect >= 1 and effect <= 7:
        if r == 0 and g == 0 and b == 0:
            #print("{} {} {}" .format(r, g, b))
            if pixel_map.rmap[index] != 0 or pixel_map.gmap[index] != 0 or pixel_map.bmap[index] != 0:
                #print (pixel_map.effectoption)
                effect_option = float(pixel_map.effectoption)
                if effect_option != 0:
                    if effect == 1:
                        r = int(round(pixel_map.rmap[index]/effect_option))
                        g = int(round(pixel_map.gmap[index]/effect_option))
                        b = int(round(pixel_map.bmap[index]/effect_option))
                    elif effect == 2:
                        r = int(round(pixel_map.rmap[index]/effect_option))
                        g = int(round(pixel_map.gmap[index]/(effect_option*lol)))
                        b = int(round(pixel_map.bmap[index]/(effect_option*lol)))
                    elif effect == 3:
                        r = int(round(pixel_map.rmap[index]/(effect_option*lol)))
                        g = int(round(pixel_map.gmap[index]/effect_option))
                        b = int(round(pixel_map.bmap[index]/(effect_option*lol)))
                    elif effect == 4:
                        r = int(round(pixel_map.rmap[index]/(effect_option*lol)))
                        g = int(round(pixel_map.gmap[index]/(effect_option*lol)))
                        b = int(round(pixel_map.bmap[index]/effect_option))
                    elif effect == 5:
                        r = int(round(pixel_map.rmap[index]/(effect_option*lol)))
                        g = int(round(pixel_map.gmap[index]/effect_option))
                        b = int(round(pixel_map.bmap[index]/effect_option))
                    elif effect == 6:
                        r = int(round(pixel_map.rmap[index]/effect_option))
                        g = int(round(pixel_map.gmap[index]/(effect_option*lol)))
                        b = int(round(pixel_map.bmap[index]/effect_option))
                    elif effect == 7:
                        r = int(round(pixel_map.rmap[index]/effect_option))
                        g = int(round(pixel_map.gmap[index]/effect_option))
                        b = int(round(pixel_map.bmap[index]/(effect_option*lol)))
                    if r < 20: r = 0
                    if g < 20: g = 0
                    if b < 20: b = 0
    pixel_map.rmap[index] = r
    pixel_map.gmap[index] = g
    pixel_map.bmap[index] = b

    if acid == True:
        ci = index - 1
        #print(ci)
        #print(pixel_map.pixel_number)
        if ci > 0 and ci < len(acidlist):
            nopbrut = acidlist[ci]
            if ci == 0: starter = 1
            else: starter = acidlist[ci - 1]
            if nopbrut <= LED_COUNT:
                #print ("{} {}" .format(starter, nopbrut))
                for i in range (starter, nopbrut, 1):
                    strip.setPixelColor(i, Color(r, g, b))

    #print("{} {} {}".format(r, g, b))

    elif pixel_map.miror:
        middle = int(round(LED_COUNT/2))
        pixel_map.pixel_number = middle
        if index > 0:
            strip.setPixelColor(middle + index , Color(r, g, b))
            strip.setPixelColor(middle - index , Color(r, g, b))
    else:

        if pixel_map.zoom != 0: zoom = pixel_map.zoom

        if zoom == 1:
            strip.setPixelColor(index, Color(r, g, b))
        else:
            for i in range (index*zoom, (index+1)*zoom, 1):
                strip.setPixelColor(i, Color(r, g, b))

def updatepixelnumber():
    pixel_map.pixel_number = int(round(LED_COUNT/pixel_map.zoom))
