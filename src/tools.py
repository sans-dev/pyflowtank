import numpy as np
import cv2

from config import pos_list


def binarize(frame,blur):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,blur,0)
    thr, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    _, mask = cv2.threshold(blur,thr,255,cv2.THRESH_BINARY_INV)
    return thr, mask

def binarize_roi(frame,blur):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thr, mask = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY_INV)
    _, mask = cv2.threshold(gray,110,255,cv2.THRESH_BINARY_INV)
    return thr, mask

def get_measurement_points(frame):
    # conversion of BGR to grayscale is necessary to apply this operation
    return np.sum(frame,axis=0)

def get_line_horizontal(x_coords,yy):
    start = (x_coords[0],yy)
    stop = (x_coords[1],yy)
    return start,stop

def get_line_vertical(xx,yy):
    start = (xx,yy[0])
    stop = (xx,yy[1])
    return start,stop

def click_event(event, x, y, flags, params):
    global pos_list
    lms = list(pos_list.keys())
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
        position =  [x,y]
        pos_list[params] = position

    # checking for right mouse clicks    
    if event==cv2.EVENT_RBUTTONDOWN: 

        del_idx = lms.index(params) - 1
        if del_idx < 0:
            # clear everything
            for key in lms:
                pos_list[key] = None

        pos_list[lms[del_idx]] = None
    return

def get_pixel_positions(frame):
    pos = np.where(frame == 255)
    return np.array(pos)

def get_upper_lower_bound(frame):
    inc_pos = []
    for col in frame.T:
        pos = np.where(col == 255)[0]
        if not pos.size:
            upper_edge = 0
            lower_edge = 0
        else:
            upper_edge = pos[0]
            lower_edge = pos[-1]
        inc_pos.append([upper_edge,lower_edge])
    return np.array(inc_pos)


def point_distance(point_a, point_b) -> float:
    diff = np.abs(point_a - point_b)
    distance = np.sqrt(np.sum(diff**2))
    return distance