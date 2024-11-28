import os
import struct
import time
import RPi.GPIO as GPIO
from animation import *
import animation
# Configuration des broches
bouton_pin = 17

# Configuration initiale de la GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(bouton_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# initialize LED animation thread
# Create a stop event object
stop_event = threading.Event()
mode =  0
thread_animate = theadAnimations(1, "Thread-Animation", mode, stop_event)

thread_animate.start()
try:
    print("Attendez que le bouton soit pressé...")
    while True:
        # r, g, b = freq_to_color3()
        # print ("{}, {}, {}" .format(r, g, b))
        if GPIO.input(bouton_pin) == GPIO.LOW:
            print("Bouton pressé!")
            # stop current animation and play the next one
            stop_event.set()
            thread_animate.mode += 1
            animation.start = False
            # Débouncing, attendez un court instant pour éviter les rebonds du bouton
            time.sleep(0.2) 
            while GPIO.input(bouton_pin) == GPIO.LOW:
                time.sleep(0.1)  # Attendez que le bouton soit relâché
        time.sleep(0.1)
except KeyboardInterrupt:
    pass

finally:
    # Nettoyer les ressources GPIO
    GPIO.cleanup()

