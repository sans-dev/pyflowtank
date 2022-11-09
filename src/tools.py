import numpy as np
import cv2
from collections import deque
from bisect import insort, bisect_left
from itertools import islice
from scipy.signal import find_peaks
from algorithms import *


def running_median_insort(seq, window_size):
    """Contributed by Peter Otten"""
    seq = iter(seq)
    d = deque()
    s = []
    result = []
    for item in islice(seq, window_size):
        d.append(item)
        insort(s, item)
        result.append(s[len(d)//2])
    m = window_size // 2
    for item in seq:
        old = d.popleft()
        d.append(item)
        del s[bisect_left(s, old)]
        insort(s, item)
        result.append(s[m])
    return result


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

def find_needle(frame,area):
    # run over the frame from top right corner and look for the first zero element
    # inctrail shoud lie within upper and lower bound
    needle_height = np.array([])
    _, mask = binarize(frame,blur=(11,11))
    n = 2
    while not needle_height.size:
        boundaries = np.where(mask[:,-n:-n+1] == 0)[0]
        if not boundaries.size:
            n += 1
            continue
        needle_height = np.where(mask[boundaries[0]:boundaries[-1],-n] == 255)[0]
        n += 1
        if n > mask.shape[0]:
            return int(mask.shape[0]/2)
    needle_height = needle_height[int(needle_height.shape[0]/2)] + boundaries[0]

    sum_pixels = np.sum(mask[needle_height-area:needle_height+area,:],axis=0)

    # search for first zero entry from right side
    needle_width = np.where(sum_pixels == 0)[0][-1]
    needle = np.array([needle_height,needle_width])
    # make new binarization of are around needle
    area = 100
    _,mask = binarize(frame[needle[0]-area:needle[0]+area,needle[1]-area:needle[1]+area],blur=(11,11))
    # search in new mask and update point
    horzontal_sum = np.sum(mask,axis=0)
    vertical_sum = np.sum(mask,axis=1)

    needle[1] = needle[1] - area + np.where(horzontal_sum > np.min(horzontal_sum))[0][0]
    needle[0] = needle[0] - area + np.where(vertical_sum == np.max(vertical_sum))[0][0]
    return needle


def get_line_horizontal(x_coords,yy):
    start = (x_coords[0],yy)
    stop = (x_coords[1],yy)
    return start,stop

def get_line_vertical(xx,yy):
    start = (xx,yy[0])
    stop = (xx,yy[1])
    return start,stop

def watershed(frame):
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    # noise removal
    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
    # sure background area
    sure_bg = cv2.dilate(opening,kernel,iterations=3)
    # Finding sure foreground area
    dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
    ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)
    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg,sure_fg)

    # Marker labelling
    ret, markers = cv2.connectedComponents(sure_fg)
    # Add one to all labels so that sure background is not 0, but 1
    markers = markers+1
    # Now, mark the region of unknown with zero
    markers[unknown==255] = 0  
    markers = cv2.watershed(frame,markers)
    frame[markers == -1] = [255,0,0]
    return frame

def kmeans(cap):
    while (cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            # release the video capture object
            cap.release()
            # Closes all the windows currently opened.
            cv2.destroyAllWindows()
            break
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        K = 5
        attempts=10

        twoDimage = frame.reshape((-1,3))
        twoDimage = np.float32(twoDimage)

        ret,label,center=cv2.kmeans(twoDimage,K,None,criteria,attempts,cv2.KMEANS_PP_CENTERS)
        center = np.uint8(center)
        res = center[label.flatten()]
        result_image = res.reshape((frame.shape))
        cv2.imshow("K means segmentation",result_image)
        # define q as the exit button
        if cv2.waitKey(10) & 0xFF == ord('q'):
            # release the video capture object
            cap.release()
            # Closes all the windows currently opened.
            cv2.destroyAllWindows()
            break

pos_list = dict(zip(['operculum','GA1','upper_jaw','lower_jaw','needle'],[None]*5))
def click_event(event, x, y, flags, params):
    landmarks = ['operculum','GA1','upper_jaw','lower_jaw','needle']
    global pos_list
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
        position =  [x,y]
        pos_list[params] = position
        # displaying the coordinates
        # on the Shell
    # checking for right mouse clicks    
    if event==cv2.EVENT_RBUTTONDOWN: 
        # displaying the coordinates
        # on the Shell
        
        # position = np.array([x,y])
        # distance = []
        # for idx,pt in pos_list.items():
        #     distance.append(point_distance(pt,position))
        del_idx = list(pos_list.keys()).index(params) - 1
        if del_idx < 0:
            return
        pos_list[landmarks[del_idx]] = None
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

def grabcut_algorithm(original_image, bounding_box):
    
    segment = np.zeros(original_image.shape[:2],np.uint8)
    
    x,y,width,height = bounding_box
    segment[y:y+height, x:x+width] = 1

    background_mdl = np.zeros((1,65), np.float64)
    foreground_mdl = np.zeros((1,65), np.float64)
    
    cv2.grabCut(original_image, segment, bounding_box, background_mdl, foreground_mdl, 5,
    cv2.GC_INIT_WITH_RECT)

    new_mask = np.where((segment==2)|(segment==0),0,1).astype('uint8')

    original_image = original_image*new_mask[:,:,np.newaxis]

    cv2.imshow('Result', original_image)


def draw_bounding_box(click, x, y, flag_param, parameters):
    global x_pt, y_pt, drawing, top_left_point, bottom_right_point, original_image  
    
    if click == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        x_pt, y_pt = x, y   

    elif click == cv2.EVENT_MOUSEMOVE:
        if drawing:
            top_left_point, bottom_right_point = (x_pt,y_pt), (x,y)
            frame[y_pt:y, x_pt:x] = 255 - original_image[y_pt:y, x_pt:x]
            cv2.rectangle(frame, top_left_point, bottom_right_point, (0,255,0), 2)
    
    elif click == cv2.EVENT_LBUTTONUP:
        drawing = False
        top_left_point, bottom_right_point = (x_pt,y_pt), (x,y)
        frame[y_pt:y, x_pt:x] = 255 - frame[y_pt:y, x_pt:x]
        cv2.rectangle(frame, top_left_point, bottom_right_point, (0,255,0), 2)
        bounding_box = (x_pt, y_pt, x-x_pt, y-y_pt)
        
        grabcut_algorithm(original_image, bounding_box)