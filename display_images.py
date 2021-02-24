# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
Be sure to check the learn guides for more usage information.

This example is for use on (Linux) computers that are using CPython with
Adafruit Blinka to support CircuitPython libraries. CircuitPython does
not support PIL/pillow (python imaging library)!

Author(s): Melissa LeBlanc-Williams for Adafruit Industries
"""

import digitalio
import board
import time
import datetime
import os
import sys
from PIL import Image, ImageDraw
import adafruit_rgb_display.st7789 as st7789

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pinA = digitalio.DigitalInOut(board.D24)
dc_pinA = digitalio.DigitalInOut(board.D23)
reset_pin = digitalio.DigitalInOut(board.D26) #noop

cs_pinB = digitalio.DigitalInOut(board.CE1)
dc_pinB = digitalio.DigitalInOut(board.D1)

cs_pinC = digitalio.DigitalInOut(board.D27)
dc_pinC = digitalio.DigitalInOut(board.D17)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# pylint: disable=line-too-long
# 1.14" ST7789

dispA = st7789.ST7789(
    spi,
    rotation=90,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40, 
    cs=cs_pinA,
    dc=dc_pinA,
    rst=reset_pin,
    baudrate=BAUDRATE,
)
dispB = st7789.ST7789(
    spi,
    rotation=90,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40, 
    cs=cs_pinB,
    dc=dc_pinB,
    rst=reset_pin,
    baudrate=BAUDRATE,
)
dispC = st7789.ST7789(
    spi,
    rotation=90,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40, 
    cs=cs_pinC,
    dc=dc_pinC,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

displays = [dispA, dispB, dispC]

def get_size(disp):
    if disp.rotation % 180 == 90:
        height = disp.width  # we swap height/width to rotate it to landscape!
        width = disp.height
    else:
        width = disp.width  # we swap height/width to rotate it to landscape!
        height = disp.height
    return (width, height)

def draw_blank(disp):
    # Create blank image for drawing.
    # Make sure to create image with mode 'RGB' for full color.
    (width, height) = get_size(disp)
    image = Image.new("RGB", (width, height))
    
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    disp.image(image)

def get_thumb_path(path):
    #prefix = os.path.split(path)[0]
    fname = os.path.splitext(path)[0]
    return '%s.thumb.jpg' % fname

def make_thumb(disp, path):
    (width, height) = get_size(disp)
    image = Image.open(path)

    # Scale the image to the smaller screen dimension
    image_ratio = image.width / image.height
    screen_ratio = width / height
    if screen_ratio < image_ratio:
        scaled_width = image.width * height // image.height
        scaled_height = height
    else:
        scaled_width = width
        scaled_height = image.height * width // image.width
    image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

    # Crop and center the image
    x = scaled_width // 2 - width // 2
    y = scaled_height // 2 - height // 2
    image = image.crop((x, y, x + width, y + height))
    image.save(get_thumb_path(path), 'JPEG')
    return image

def get_thumb(disp, path):
    try:
        img = Image.open(get_thumb_path(path))
        return img
    except IOError:
        return make_thumb(disp, path)


def draw_image(disp, path):
    # Display image.
    disp.image(get_thumb(disp, path))

def get_image_key(fname):
    split = fname.split('.')
    time = datetime.datetime.strptime(split[0], '%Y-%m-%d_%H-%M').timestamp()
    return '%s.%s' % (time, split[1])


dirname = 'images' 
images = os.listdir(dirname)
images = [image for image in images if 'thumb' not in image]
images.sort(key=get_image_key)
images_by_set = []
cur_set = []
for image in images:
    if len(cur_set) == len(displays):
        images_by_set.append(cur_set)
        cur_set = []
    cur_set.append('%s/%s'% (dirname, image))
    # check for consistent naming
    for fname in cur_set:
        if fname.split('.')[0] != cur_set[0].split('.')[0]:
            raise BaseException("inconsistent naming arount %s" % fname)


for disp in displays:
    draw_blank(disp)
time.sleep(2)

set_num = 0

while True:
    start = time.time()
    if (set_num == len(images_by_set) - 1):
        set_num = 0
    for display, image in zip(displays, images_by_set[set_num]):
        draw_image(display, image)
    
    print('drew images in %f seconds' % (time.time() - start))
    set_num += 1
