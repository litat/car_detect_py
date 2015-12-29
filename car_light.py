# import sys
import cv2
import numpy as np


class CarLight(object):
	"""docstring for CarLight"""
	def __init__(self):
		pass

	controlWindowName = "Control"
	iHiH = 35
	iLoH = 0
	iHiS = 255
	iLoS = 0
	iHiV = 255
	iLoV = 127

	contours_polys = None
	circles = None

	sourceImage = None
	thresholdImage = None
	outputImage = None

	output_rectangles = []

	def getImage(self, image):
		self.sourceImage = image
		self.initImageSize(image)

	def filterCarLight(self):
		self.filterThreshold()
		self.filterContours()
		return self.output_rectangles

	def filterThreshold(self):
		hsvImage = cv2.cvtColor(self.sourceImage, cv2.COLOR_BGR2HSV)
		self.thresholdImage = cv2.inRange(hsvImage,
		                                  (self.iLoH, self.iLoS, self.iLoV),
		                                  (self.iHiH, self.iHiS, self.iHiV))
		self.thresholdImage = cv2.erode(self.thresholdImage,
		                                cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
		self.thresholdImage = cv2.dilate(self.thresholdImage,
		                                 cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

	def filterContours(self):
		contours, _ = cv2.findContours(self.thresholdImage.copy(),
		                               cv2.RETR_TREE,
		                               cv2.CHAIN_APPROX_SIMPLE)
		self.contours_polys = []
		self.circles = []
		self.output_rectangles = []
		for contour in contours:
			contours_poly = cv2.approxPolyDP(contour, 3, True)
			self.contours_polys.append(contours_poly)
			center, radius = cv2.minEnclosingCircle(contours_poly)
			if radius > 20:
				circle = (center, radius)
				rect = turnCircle2Rect(circle)
				self.output_rectangles.append(rect)

	def initImageSize(self, image):
		self.outputImage = np.zeros(image.shape, np.uint8)


def turnCircle2Rect(circle):
	center, radius = circle
	center_x, center_y = center
	rect_x = center_x -radius
	rect_y = center_y -radius
	rect_w = 2*radius
	rect_h = 2*radius
	return [rect_x, rect_y, rect_w, rect_h]
