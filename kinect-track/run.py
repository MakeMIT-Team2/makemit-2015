import freenect, sys, frame_convert, cv, time, math
import numpy as np
import cv2

cv.NamedWindow('Depth')
cv.NamedWindow('Video')

mx = False
my = False

threshold = 20
fgbg = cv2.BackgroundSubtractorMOG()

def update_depth():
	depth, timestamp = freenect.sync_get_depth()
	return frame_convert.pretty_depth_cv(depth)

def update_frame():
	frame, timestamp = freenect.sync_get_video()
	# a = -1
	# b = -1
	# for i in frame:
	# 	a = a + 1
	# 	b = -1
	# 	for j in i:
	# 		b = b + 1
	# 		if j[0] > 47 and j[0] < 100 and j[1] > 177 and j[2] > 220:
	# 			frame[a][b] = [0, 0, 255]
	# dst = np.array(frame)
	lowerBound = cv.Scalar(30, 120, 220);
	upperBound = cv.Scalar(104, 230, 255);
	fgmask = fgbg.apply(frame)
	frame = cv2.bitwise_and(frame,frame,mask=fgmask)
	frame = cv2.inRange(frame, lowerBound, upperBound);
	contours, hier = cv2.findContours(frame,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
	x_av = 0
	y_av = 0
	n = 0
	for cnt in contours:
		if 5<cv2.contourArea(cnt):
			for i in cnt:
				n = n + 1
				x_av = x_av + i[0][0]
				y_av = y_av + i[0][1]
			break
	if n > 0:
		x_av = x_av/n
		y_av = y_av/n
		print (x_av, y_av)
	# for i in range(len(frame)):
	# 	for j in range(len(frame[i])):
	# 		frame[i][j] = np.bitwise_and(frame[i][j], fgmask[i][j])
	
	# frame.copyTo(dst, fgmask)
	# cv.Copy(frame, frame, mask=fgmask)
	# frame = cv2.bitwise_and(frame, fgmask)
	return frame

def get_xyz(depth, px, py):
	RANGE_X = 0
	RANGE_Y = 0
	RANGE_DEPTH = 4
	MAX_PX = 640
	MAX_PY = 480
	# 50cm to 4m
	# should figure out what the x/y shit looks like at 4m away
	m_depth = (0.1236 * math.tan(rawDisparity / 2842.5 + 1.1863)) * 100
	x = -(RANGE_X * ((MAX_PX/2 - px)/MAX_PX) * (m_depth/RANGE_DEPTH)) + (RANGE_X/2)
	y = -(RANGE_Y * ((MAX_PY/2 - py)/MAX_PY) * (m_depth/RANGE_DEPTH)) + (RANGE_Y/2)
	z = m_depth

	return [x, y, z]

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
	frame = update_frame()
	cv.ShowImage('Depth', update_depth())
	cv2.imshow('Video', frame)
	if cv.WaitKey(10) == 27:
		break

# things we would do if we had more time:
	# calibrate for the fields of view in opencv
	# normalize depth readings