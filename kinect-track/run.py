import freenect, sys, cv, time, math
import numpy as np
import cv2

from socketIO_client import SocketIO, LoggingNamespace

socketIO = SocketIO('0.0.0.0', 8080, LoggingNamespace)

cv.NamedWindow('Depth')
cv.NamedWindow('Video')
lastcoords = [0, 0]
mx = False
my = False

threshold = 20
fgbg = cv2.BackgroundSubtractorMOG()

def update_depth():
	depth, timestamp = freenect.sync_get_depth()
	return depth

def update_frame():
	frame, timestamp = freenect.sync_get_video()

	lowerBound = cv.Scalar(255, 255, 255);
	upperBound = cv.Scalar(255, 255, 255);
	frame = cv2.inRange(frame, lowerBound, upperBound);
	fgmask = fgbg.apply(frame)
	frame = cv2.bitwise_and(frame,frame,mask=fgmask)
	contours, hier = cv2.findContours(frame,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
	x_av = 0
	y_av = 0
	n = 0
	coord_candidates = []
	for cnt in contours:
		n =0
		x_av = 0
		y_av = 0
		for i in cnt:
			n = n + 1
			x_av = x_av + i[0][0]
			y_av = y_av + i[0][1]
		x_av = float(x_av)/n
		y_av = float(y_av)/n
		coord_candidates.append([x_av, y_av])

	if len(coord_candidates) > 0:
		best = [99999999, 0, 0]
		for i in coord_candidates:
			dist = (i[0] - lastcoords[0]) * (i[0] - lastcoords[0]) + (i[1] - lastcoords[1]) * (i[1] - lastcoords[1])
			if dist < best[0]:
				best = [dist, i[0], i[1]]
		return frame, best[1], best[2]

	return frame, False, False

def get_xyz(depth, px, py):
	depth = float(depth)
	px = float(px)
	py = float(py)
	RANGE_X = 4.318
	RANGE_Y = 3.2385
	CORRECTION_Y = -0.301135642301
	RANGE_DEPTH = 3.6068
	MAX_PX = 640.0
	MAX_PY = 480.0
	# 50cm to 4m
	# should figure out what the x/y shit looks like at 4m away
	m_depth = (0.1236 * math.tan(depth / 2842.5 + 1.1863)) #depth in centimeters
	x = -(RANGE_X * ((MAX_PX/2 - px)/MAX_PX) * (m_depth/RANGE_DEPTH)) + (RANGE_X/2)
	y = -(RANGE_Y * ((MAX_PY/2 - py)/MAX_PY) * (m_depth/RANGE_DEPTH)) + (RANGE_Y/2) + CORRECTION_Y
	z = m_depth

	return [x, y, z]

def get_av_depth(x, y):
	n = 0
	su = 0
	s = get_depth_at_point(x, y)
	if s > 0:
		n = n + 1
		su = su + s

	s = get_depth_at_point(x+1, y)
	if s > 0:
		n = n + 1
		su = su + s

	s = get_depth_at_point(x, y+1)
	if s > 0:
		n = n + 1
		su = su + s

	s = get_depth_at_point(x+1, y+1)
	if s > 0:
		n = n + 1
		su = su + s

	s = get_depth_at_point(x-1, y)
	if s > 0:
		n = n + 1
		su = su + s

	s = get_depth_at_point(x, y-1)
	if s > 0:
		n = n + 1
		su = su + s

	s = get_depth_at_point(x-1, y-1)
	if s > 0:
		n = n + 1
		su = su + s

	s = get_depth_at_point(x-1, y+1)
	if s > 0:
		n = n + 1
		su = su + s

	s = get_depth_at_point(x+1, y-1)
	if s > 0:
		n = n + 1
		su = su + s

	if n == 0:
		return 0
	return float(su)/n

def get_depth_at_point(x, y):
	if x < 631 and y < 480 and y > -1 and x > -1:
		d = depth[y][x]
		if d > 2040:
			return 0
		return d 
	return 0

#depth
	# array of arrays
	# first index = y value
	# second index = x value
	# 0,0 is the top left
	# indices 632-640 don't work
		# 631-639
	# 2047

#color
	# 480 * 640
	# array of arrays
	# first index = y value
	# second index = x value
	# 0,0 is the top left

# cv.CreateTrackbar('threshold', 'Video', bval, 200,  change_bval)

while True:
	frame, px, py = update_frame()
	depth = update_depth()
	if not px == False:
		depth = get_av_depth(px, py)
		if depth > 0:
			x, y, z = get_xyz(depth, px, py)
			socketIO.emit('pos', {
				'x':x,
				'y':y,
				'z':z
			})
			print x, y, z
	cv2.imshow('Depth', depth)
	cv2.imshow('Video', frame)
	if cv.WaitKey(10) == 27:
		break

# things we would do if we had more time:
	# calibrate for the fields of view in opencv
	# normalize depth readings