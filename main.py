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

# --- enter values for calibration --------------------------------------------

COL_FLOOR = 30
COL_LINE = 60

RGB_DRIVE_RIGHT = (250, 250, 250)
RGB_DRIVE_LEFT = (30, 30, 30)
RGB_WITHIN_PERCENTAGE = 0.05

# speed an angle can be increased and decreased depending on steepens of 
# the curves in the line
SPEED = 70
ANGLE = 30

# values for driving around the object - heavily depends on outcome
OBSTACLE_BACKWARDS_LENGTH = -30
BACK_ON_LINE_FORWARD_LENGTH = 85
TURN_RATE_ON_BACK_ON_LINE = 60
TURN_RATE_ON_DRIVE_AROUND = 90
TURN_SPEED = 100
TURN_ANGLE = 30

# wait times
WAIT_TIME_EACH_CYCLE = 50
WAIT_TIME_CYCLE = 1000

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
BREAK = 0
FINISH = 1
FOLLOW_LINE = 2
DRIVE_LEFT = 3
DRIVE_RIGHT = 4

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
# end print_state

def is_color_within_range(color1, color2, range_percent):
    for component1, component2 in zip(color1, color2):
        min_value = component2 - (component2 * range_percent)
        max_value = component2 + (component2 * range_percent)
        if component1 < min_value or component1 > max_value:
            return False
    return True
# end is_color_within_range

def drive_around_object():
    global current_state
    print_state()

    robot.straight(OBSTACLE_BACKWARDS_LENGTH)

    turn_rate = TURN_RATE_ON_DRIVE_AROUND if current_state == DRIVE_RIGHT else -TURN_RATE_ON_DRIVE_AROUND
    robot.turn(turn_rate)

    drive_around_angle = TURN_ANGLE if current_state == DRIVE_LEFT else -TURN_ANGLE
    robot.drive(TURN_SPEED, drive_around_angle)

    wait(WAIT_TIME_AFTER_START_DRIVE_AROUND)
# end drive_around_object

def handle_collision():
    global current_state

    if is_color_within_range(RGB_DRIVE_RIGHT, front_color_sensor.rgb(), 
                            RGB_WITHIN_PERCENTAGE):
        current_state = DRIVE_LEFT
        drive_around_object()

    elif is_color_within_range(RGB_DRIVE_LEFT, front_color_sensor.rgb(), 
                            RGB_WITHIN_PERCENTAGE):
        current_state = DRIVE_RIGHT
        drive_around_object()

    else:
        robot.stop()
        current_state = BREAK
# end handle_collision

def check_surroundings():
    global current_state

    # edge in front of robot detected
    if edge_infrared_sensor.distance() > 10:
        robot.stop()
        current_state = BREAK

    # object in front of robot 
    if current_state == FOLLOW_LINE and colli_sonic_sensor.distance() < 40:
        handle_collision()
# end check_surroundings

def back_on_line():
    global current_state

    robot.straight(BACK_ON_LINE_FORWARD_LENGTH)

    turn_rate = (TURN_RATE_ON_BACK_ON_LINE if current_state == DRIVE_LEFT
                else -TURN_RATE_ON_BACK_ON_LINE)
    robot.turn(turn_rate)

    current_state = FOLLOW_LINE
# end back_on_line

def follow_line():
    if bot_color_sensor.reflection() < COL_THRESHOLD:
        robot.drive(SPEED,ANGLE)
    else:
        robot.drive(SPEED,ANGLE * -1)
# end follow_line

# --- main loop ---------------------------------------------------------------
while True:
    check_surroundings()
    print_state()

    if current_state == BREAK or current_state == FINISH:
        ev3.speaker.beep()
        break
    
    elif current_state == FOLLOW_LINE:
        follow_line()

    elif current_state == DRIVE_LEFT or current_state == DRIVE_RIGHT:
        if bot_color_sensor.reflection() > COL_THRESHOLD:
            back_on_line()
        else:
            turn_angle = TURN_ANGLE if current_state == DRIVE_LEFT else -TURN_ANGLE
            robot.drive(TURN_SPEED, turn_angle)
    
    wait(WAIT_TIME_CYCLE)
