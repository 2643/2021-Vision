#!/usr/bin/env python3
from collections import deque
from networktables import NetworkTables
# from sympy import Interval, Union # not performant enough with multiple interval joins.
import sys
import numpy as np
import threading
import cv2
import imutils
import time

CONNECT_TO_SERVER = True
# Normal image, Filter image
DEBUG = {
    'dshow': True,
    'fakeNetworkTables': True,
    'show_img': True,
    'show_filter': True,
    'show_centroid': True,
    'show_centers': {
        'blue': True,
        'red': True
    },
    'show_max_box': {
        'blue': True,
        'red': True	
    },
    'show_lines': {
        'blue': True,
        'red': True	
    },
    'draw_normal_box': {
        'blue': True,
        'red': True	
    },
    'show_trails': False,
    'rotate': True
}
REQ_CLOSEST = True
CENTER_BAND = 100
HORIZONTAL_OFFSET = 100
BUFFER_LEN = 32
ROT_ANGLE = 180
ROT_SCALE = 1.0

def connect():
    cond = threading.Condition()
    notified = [False]

    def connectionListener(connected, info):
        print(info, '; Connected=%s' % connected)
        with cond:
            notified[0] = True
            cond.notify()

    NetworkTables.initialize(server='roborio-2643-frc.local')
    NetworkTables.addConnectionListener(
        connectionListener, immediateNotify=True)

    with cond:
        print("Waiting")
        if not notified[0]:
            cond.wait()

    return NetworkTables.getTable('gs-vision-table-marker')


if CONNECT_TO_SERVER:
    if not DEBUG['fakeNetworkTables']:
        table = connect()
    else:
        table = open('gs_markerfakenetworktable.txt', 'w+')
    DEBUG = {
        'dshow': False,
        'fakeNetworkTables': DEBUG['fakeNetworkTables'],
        'show_img': False,
        'show_filter': False,
        'show_centroid': False,
        'show_centers': {
            'blue': False,
            'red': False
        },
        'show_max_box': {
            'blue': False,
            'red': False	
        },
        'show_lines': {
            'blue': False,
            'red': False	
        },
        'draw_normal_box': {
            'blue': False,
            'red': False	
        },
        'show_trails': False,
        'rotate': True
    }

# TODO: make cyan by image color inversion... perhaps
# Invert and convert to HSV

# img_hsv=cv2.cvtColor(255-img, cv2.COLOR_BGR2HSV) 

# # Mask all red pixels (cyan in inverted image)
# lo = np.uint8([80,30,0]) 
# hi = np.uint8([95,255,255])  

# mask = cv2.inRange(img_hsv,lo,hi)

redLowerOne = (170, 128, 32)    # TODO: get vals. 
redUpperOne = (179, 255, 255) # TODO: get vals. 
redLowerTwo = (0, 128, 32)    # TODO: get vals. 
redUpperTwo = (5, 255, 255) # TODO: get vals. 

blueLower = (105, 80, 64)     # TODO: get vals. higher saturation I think. b/c MPR light blue.
blueUpper = (130, 255, 255)   # TODO: get vals. 

minArea = 150 # 10 TODO: tune.
red_pts = deque(maxlen=BUFFER_LEN)
blue_pts = deque(maxlen=BUFFER_LEN)

if DEBUG['dshow'] and sys.platform.startswith('win32'):
    vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)
elif DEBUG['dshow'] and sys.platform.startswith('linux'):
    vs = cv2.VideoCapture(2)
else:
    vs = cv2.VideoCapture(21)

if not CONNECT_TO_SERVER and sys.platform.startswith('win32'):
    vs.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
    vs.set(cv2.CAP_PROP_EXPOSURE, -7)
    vs.set(cv2.CAP_PROP_FPS, 30)

time.sleep(1.0)

img_x_size = int(vs.get(cv2.CAP_PROP_FRAME_WIDTH))
img_y_size = int(vs.get(cv2.CAP_PROP_FRAME_HEIGHT))
img_center = (img_x_size//2, img_y_size//2)

valid_ctr = -1
while True:
    frame = vs.read()
    frame = frame[1]
    if DEBUG['rotate']:
        frame = cv2.rotate(frame, cv2.ROTATE_180)

    # frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    red_mask_one = cv2.inRange(hsv, redLowerOne, redUpperOne)
    red_mask_two = cv2.inRange(hsv, redLowerTwo, redUpperTwo)
    red_mask = red_mask_one + red_mask_two
    if DEBUG['show_filter']:
        #cv2.imshow("red_filter_one", red_mask_one)
        #cv2.imshow("red_filter_two", red_mask_two)
        cv2.imshow("red_filter", red_mask)
    red_mask = cv2.erode(red_mask, None, iterations=2)
    red_mask = cv2.dilate(red_mask, None, iterations=2)
    
    red_cnts = cv2.findContours(red_mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    red_cnts = imutils.grab_contours(red_cnts)

    # only proceed if at least one contour was found
    valid_red_cnts = []
    if len(red_cnts) > 0:
        for c in red_cnts:
            M = cv2.moments(c)
            red_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if M["m00"] > minArea:
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                valid_red_cnts.append({
                    'contour': c,
                    'left_edge': min(box[0][0], box[3][0]),
                    'right_edge': max(box[1][0], box[2][0]),
                    'top_edge': min(box[0][1], box[1][1]),
                    'bottom_edge': min(box[2][1], box[3][1]),
                    'center': red_center,
                    'box': box
                })
    else:
        red_center = None

    blue_mask = cv2.inRange(hsv, blueLower, blueUpper)
    if DEBUG['show_filter']:
        cv2.imshow("blue_filter", blue_mask)
    blue_mask = cv2.erode(blue_mask, None, iterations=2)
    blue_mask = cv2.dilate(blue_mask, None, iterations=2)

    # find contours in the mask
    blue_cnts = cv2.findContours(blue_mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    blue_cnts = imutils.grab_contours(blue_cnts)
    
    center = None
    # only proceed if at least one contour was found
    valid_blue_cnts = []
    if len(blue_cnts) > 0:
        for c in blue_cnts:
            M = cv2.moments(c)
            blue_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if M["m00"] > minArea:
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                box = np.int0(box)

                for red_c in valid_red_cnts:
                    if blue_center[0] >= red_c['left_edge'] and blue_center[0] <= red_c['right_edge'] and blue_center[1] <= red_c['top_edge']:
                        valid_blue_cnts.append({
                            'contour': c,
                            'left_edge': min(box[0][0], box[3][0]),
                            'right_edge': max(box[1][0], box[2][0]),
                            'top_edge': min(box[0][1], box[1][1]),
                            'bottom_edge': min(box[2][1], box[3][1]),
                            'center': blue_center,
                            'box': box
                        })
                        if DEBUG['show_img'] and DEBUG['draw_normal_box']['blue']:
                            cv2.drawContours(frame, [box], 0, (255, 0, 0), 2)
                        break
    else:
        blue_center = None

    to_rm = []
    for ind, red_c in enumerate(valid_red_cnts):
        in_range = False
        for blue_c in valid_blue_cnts:
            if red_c['center'][0] >= blue_c['left_edge'] and red_c['center'][0] <= blue_c['right_edge'] and red_c['center'][1] >= blue_c['bottom_edge']:
                in_range = True
                break
        if not in_range:
            to_rm.append(ind)
        else:
            if DEBUG['show_img'] and DEBUG['draw_normal_box']['red']:
                cv2.drawContours(frame, [red_c['box']], 0, (0, 0, 255), 2)

    for ind in sorted(to_rm, reverse=True):
        valid_red_cnts.pop(ind)

    if REQ_CLOSEST:
            #track the largest
            valid = True
            if len(valid_blue_cnts) > 0:
                c = max([datapack for datapack in valid_blue_cnts], key=lambda dc: cv2.contourArea(dc['contour']))
                box = c['box']

                if DEBUG['show_img']:
                    if DEBUG['show_lines']['blue']:
                        frame = cv2.line(frame,(min(box[0][0], box[3][0]), 0),
                                (min(box[0][0], box[3][0]), img_y_size),(252, 3, 119),3)
                        frame = cv2.line(frame,(max(box[1][0], box[2][0]), 0),
                                (max(box[1][0], box[2][0]), img_y_size),(252, 3, 119),3)
                    if DEBUG['show_max_box']['blue']:
                        cv2.drawContours(frame, [box], 0, (255, 0, 0), 2)
                blue_max_c = c
            else: valid = False

            if len(valid_red_cnts) > 0:
                c = max([datapack for datapack in valid_red_cnts], key=lambda dc: cv2.contourArea(dc['contour']))
                box = c['box']

                if DEBUG['show_img']:
                    if DEBUG['show_lines']['red']:
                        frame = cv2.line(frame,(min(box[0][0], box[3][0]), 0),
                                (min(box[0][0], box[3][0]), img_y_size),(252, 3, 119),3)
                        frame = cv2.line(frame,(max(box[1][0], box[2][0]), 0),
                                (max(box[1][0], box[2][0]), img_y_size),(252, 3, 119),3)
                    if DEBUG['show_max_box']['red']:
                        cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
                red_max_c = c
            else: valid = False
            
            if valid:
                valid_ctr = 15
                center_avg = ((red_max_c['center'][0] + blue_max_c['center'][0])//2, (red_max_c['center'][1] + blue_max_c['center'][1])//2)
                if DEBUG['show_max_box']['blue'] and DEBUG['show_max_box']['red']:
                    cv2.circle(frame, center_avg, 5, (0, 255, 0), -1)
            
    if valid_ctr >= 0:
        valid_ctr -= 1
    else:
        center_avg = None

    if CONNECT_TO_SERVER and REQ_CLOSEST:
        if not DEBUG['fakeNetworkTables']:
            if center_avg is None and valid_ctr < 0:
                table.putBoolean('has_target', False)
                table.putBoolean('near', False)
            else:
                table.putBoolean('has_target', True)
                if center_avg[0] < (img_center[0] - CENTER_BAND):
                    table.putNumber('left_exceeded', ((img_center[0] - CENTER_BAND) - center_avg[0]))
                else:
                    table.putNumber('left_exceeded', 0)

                if center_avg[0] > (img_center[0] + CENTER_BAND):
                    table.putNumber('right_exceeded', (center_avg[0] - (img_center[0] + CENTER_BAND)))
                else:
                    table.putNumber('right_exceeded', 0)
                
                if center_avg[1] < (img_center[1] + HORIZONTAL_OFFSET):
                    table.putBoolean('near', True)
                else:
                    table.putBoolean('near', False)
        else:
            table.write(str(center_avg).ljust(15) + "  " + str(valid_ctr).ljust(5) + '\n')
            table.flush()


    if DEBUG['show_img']:
        if REQ_CLOSEST and valid and DEBUG['show_trails']:
            red_pts.appendleft(red_max_c['center'])

            # loop over the set of tracked points
            for i in range(1, len(red_pts)):
                # if either of the tracked points are None, ignore
                # them
                if red_pts[i - 1] is None or red_pts[i] is None:
                    continue

                # otherwise, compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(BUFFER_LEN / float(i + 1)) * 2.5)
                cv2.line(frame, red_pts[i - 1], red_pts[i], (0, 0, 255), thickness)

            blue_pts.appendleft(blue_max_c['center'])

            # loop over the set of tracked points
            for i in range(1, len(blue_pts)):
                # if either of the tracked points are None, ignore
                # them
                if blue_pts[i - 1] is None or blue_pts[i] is None:
                    continue

                # otherwise, compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(BUFFER_LEN / float(i + 1)) * 2.5)
                cv2.line(frame, blue_pts[i - 1], blue_pts[i], (255, 0, 0), thickness)
        elif not valid and DEBUG['show_trails']:
            red_pts.appendleft(None)
            blue_pts.appendleft(None)

        # show the frame to our screen
        if DEBUG['show_centers']['red']:
            for c in valid_red_cnts:
                cv2.circle(frame, c['center'], 5, (0, 0, 255), -1)
        
        if DEBUG['show_centers']['blue']:
            for c in valid_blue_cnts:
                cv2.circle(frame, c['center'], 5, (255, 130, 50), -1)

        cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

vs.release()
cv2.destroyAllWindows()

if CONNECT_TO_SERVER and DEBUG['fakeNetworkTables']:
    table.truncate(0)