#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, ColorSensor as Ev3ColorSensor,
                                 InfraredSensor, UltrasonicSensor)
from pybricks.nxtdevices import ColorSensor as NXTColorSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.

ev3 = EV3Brick()

front_color_sensor = NXTColorSensor(Port.S1)
bot_color_sensor = Ev3ColorSensor(Port.S4)
edge_infrared_sensor = InfraredSensor(Port.S3)
colli_sonic_sensor = UltrasonicSensor(Port.S2)

while True:
    ev3.screen.clear()
    ev3.screen.draw_text(0, 10, 'front-col: {}'.format(front_color_sensor.color()))
    ev3.screen.draw_text(0, 25, 'front-rgb: {}'.format(front_color_sensor.rgb()))
    ev3.screen.draw_text(0, 40, 'bot-refl: {}'.format(bot_color_sensor.reflection()))
    ev3.screen.draw_text(0, 55, 'edge-dist: {}'.format(edge_infrared_sensor.distance()))
    ev3.screen.draw_text(0, 70, 'front-dist: {}'.format(colli_sonic_sensor.distance()))
    
    wait(100)