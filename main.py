#!/usr/bin/env pybricks-micropython
# doc: https://pybricks.com/ev3-micropython/nxtdevices.html#nxt-color-sensor
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, ColorSensor as Ev3ColorSensor,
                                 InfraredSensor, UltrasonicSensor)
from pybricks.nxtdevices import ColorSensor as NXTColorSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

# --- enter values from calibration here -------------------------------------

COL_FLOOR = 30
COL_LINE = 60

RGB_DRIVE_RIGHT = (250, 250, 250)
RGB_DRIVE_LEFT = (30, 30, 30)
RGB_WITHIN_PERCENTAGE = 0.05

# speed an angle can be increased and decreased depending on steepens of 
# the curves in the line
SPEED = 70 
ANGLE = 30

# --- Initializations ---------------------------------------------------------
ev3 = EV3Brick()

front_color_sensor = NXTColorSensor(Port.S1)
bot_color_sensor = Ev3ColorSensor(Port.S4)
edge_infrared_sensor = InfraredSensor(Port.S3)
colli_sonic_sensor = UltrasonicSensor(Port.S2)

left_motor = Motor(Port.A)
right_motor = Motor(Port.D)

COL_THRESHOLD = (COL_FLOOR + COL_LINE) / 2

robot = DriveBase(left_motor, right_motor, wheel_diameter=42, axle_track=140)

# possible states at runtime (ev3 doesn't know enums >.>)
# BREAK = 0
# FINISH = 1
# FOLLOW_LINE = 2
# DRIVE_LEFT = 3
# DRIVE_RIGHT = 4

global current_state 
current_state = 2

# --- functions ---------------------------------------------------------------

def print_state():
    global current_state
    states = {
        0: "break",
        1: "finished",
        2: "follow line",
        3: "driving right",
        4: "driving left"
    }
    ev3.screen.clear()
    ev3.screen.draw_text(0, 10, states.get(current_state, "Unknown"))

def is_color_within_range(color1, color2, range_percent):
    for component1, component2 in zip(color1, color2):
        min_value = component2 - (component2 * range_percent)
        max_value = component2 + (component2 * range_percent)
        if component1 < min_value or component1 > max_value:
            return False
    return True

def handle_collision():
    global current_state
    # a lot of magic numbers happen here, outcome heavily depends on 
    # correct calibration here - a lot of testing is needed
    if is_color_within_range(RGB_DRIVE_RIGHT, front_color_sensor.rgb(), 
                            RGB_WITHIN_PERCENTAGE):
        current_state = 3
        print_state()
        robot.straight(-30)
        robot.turn(90)
        robot.drive(100, -30)
        wait(2000)
    elif is_color_within_range(RGB_DRIVE_LEFT, front_color_sensor.rgb(), 
                            RGB_WITHIN_PERCENTAGE):
        current_state = 4
        print_state()
        robot.straight(-30)
        robot.turn(-90)
        robot.drive(100, 30)
        wait(1000)
    else:
        robot.stop()
        current_state = 0
        # current_state = 3
        # print_state()
        # robot.straight(-30)
        # robot.turn(90)
        # robot.drive(100, -30)
        # wait(1000)

def check_surroundings():
    global current_state
    if edge_infrared_sensor.distance() > 10:
        robot.stop()
        current_state = 0

    # a lot of magic numbers happen here, outcome heavily depends on 
    # correct calibration here - a lot of testing is needed
    if current_state == 2 and colli_sonic_sensor.distance() < 40:
        handle_collision()
    elif current_state == 3 and bot_color_sensor.reflection() > COL_THRESHOLD:
        robot.straight(85)
        robot.turn(60)
        current_state = 2
    elif current_state == 4 and bot_color_sensor.reflection() > COL_THRESHOLD:
        robot.straight(85)
        robot.turn(-60)
        current_state = 2

def follow_line():
    if bot_color_sensor.reflection() < COL_THRESHOLD:
        robot.drive(SPEED,ANGLE)
    else:
        robot.drive(SPEED,ANGLE * -1)

# --- main loop ---------------------------------------------------------------
while True:
    check_surroundings()
    print_state()

    if current_state == 0 or current_state == 1:
        ev3.speaker.beep()
        break
    elif current_state == 2:
        follow_line()
    elif current_state == 3:
        robot.drive(100, -30)
    elif current_state == 4:
        robot.drive(100, 30)
    
    wait(50)
