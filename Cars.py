import math
import cv2
import cv
import numpy as np
import car_cascade as cc
import car_light as cl


class Cars(object):
	"""docstring for Cars"""
	def __init__(self):
		self.car_cascade = cc.CarCascade()
		self.car_light = cl.CarLight()

	sourceImage = None
	filterImage = None
	mainOutput = None

	my_v = 30
	otherV = 80

	notifyDistance = 100

	is_day = False

	myVTrackbarName = "My Velocity"
	notifyDistanceTrackbarName = "Notify Distance"
	mainOutputWindowName = "Display Output"

	def getImage(self, image):
		if image is None:
			print "image not filled"
			return
		self.sourceImage = image
		self.mainOutput = image
		self.car_cascade.getImage(image)
		self.car_light.getImage(image)

	def findcars(self):
		self.car_light.filterCarLight()
		self.car_cascade.filterCars()
		self.is_day = np.mean(self.car_light.thresholdImage) > 20

		if self.is_day:
			output_rectangles = self.car_cascade.output_rectangles
			self.filterImage = self.mainOutput
		else:
			output_rectangles = self.car_light.output_rectangles
			self.filterImage = np.zeros(self.mainOutput.shape, np.uint8)
		self.drawMarks(output_rectangles)

	def drawMarks(self, rectangles):
		rectangles = np.array(rectangles).tolist()
		rectangles, _ = cv2.groupRectangles(rectangles, 0, 100)
		for rect in rectangles:
			distance = calDistance(rect)
			rect_x, rect_y, width = getRectXYWitdth(rect)
			if distance < self.notifyDistance:
				color = (0, 0, 255)
				self.drawExclamationMark(rect_x, rect_y, width, color)
			elif self.my_v > self.otherV:
				color = (0, 0, 255)
				self.drawExclamationMark(rect_x, rect_y, width, color)
			elif self.my_v > distance / 2:
				color = (0, 0, 255)
				self.drawExclamationMark(rect_x, rect_y, width, color)
			else:
				color = (0, 255, 0)
				self.drawRectangle(rect, color)

	def drawRectangle(self, rect, color):
		# blank = np.zeros(self.mainOutput.shape, np.uint8)
		width = rect[2] / 40
		pt1 = (rect[0], rect[1])
		pt2 = (rect[0] + rect[2], rect[1] + rect[3])
		cv2.rectangle(self.filterImage, pt1, pt2, color, width)
		# self.mainOutput = cv2.addWeighted(self.filterImage, 1, blank, 0.5, 0)

	def drawExclamationMark(self, rect_x, rect_y, rect_width, color):
		times = rect_width
		blank = np.zeros(self.mainOutput.shape, np.uint8)

		exclamationMarkUpper = [
		                [-2 * times + rect_x, -8 * times + rect_y],
		                [-2 * times + rect_x, 1 * times + rect_y],
		                [2 * times + rect_x, 1 * times + rect_y],
		                [2 * times + rect_x, -8 * times + rect_y]]
		exclamationMarkLower = [
		                [-2 * times + rect_x, 3 * times + rect_y],
		                [-2 * times + rect_x, 7 * times + rect_y],
		                [2 * times + rect_x, 7 * times + rect_y],
		                [2 * times + rect_x, 3 * times + rect_y]]
		exclamationMarkUpper = np.array(exclamationMarkUpper, np.int32)
		exclamationMarkLower = np.array(exclamationMarkLower, np.int32)

		cv2.fillPoly(self.filterImage, [exclamationMarkUpper], color)
		cv2.fillPoly(self.filterImage, [exclamationMarkLower], color)

		# self.mainOutput = cv2.addWeighted(self.filterImage, 1, blank, 1, 0)

	def display_output(self):
		if self.mainOutput is None:
			return
		self.merge_outputs()
		# self.display_text()
		cv2.imshow(self.mainOutputWindowName, self.mainOutput)
		# self.display_trackbar()

	def merge_outputs(self):
		if not self.is_day:
			self.mainOutput = cv2.addWeighted(self.mainOutput, 1, self.filterImage, 1, 0)

	def display_text(self):
		cv2.putText(self.mainOutput, "My Velocity: " + str(self.my_v),
		            (0, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv2.CV_AA)
		cv2.putText(self.mainOutput, "Other's Velocity: " + str(self.otherV),
		            (0, 40), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv2.CV_AA)
		cv2.putText(self.mainOutput,
		            "Notify Distance: " + str(self.notifyDistance),
		            (0, 60), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv2.CV_AA)

	def display_trackbar(self):
		cv.CreateTrackbar(self.myVTrackbarName,
		                  self.mainOutputWindowName,
		                  self.my_v, 200, self.whenMyVTrackbarChange)
		cv.CreateTrackbar(self.notifyDistanceTrackbarName,
		                  self.mainOutputWindowName,
		                  self.notifyDistance, 100, self.whenNotifyDistanceChange)

	def whenMyVTrackbarChange(self, value):
		self.my_v = value

	def whenNotifyDistanceChange(self, value):
		self.notifyDistance = value


def getRectXYWitdth(rect):
	rect_x = rect[0] + rect[2] / 2
	rect_y = rect[1] + rect[3] / 2
	width = (rect[2] / 30, 0)[0]
	return rect_x, rect_y, width


def calDistance(rect):
	width = rect[2]
	return 2272.6 * math.pow(width, -0.9776)
