import sys
import cv2
import cv
import numpy as np
import math


class Cars(object):
	"""docstring for Cars"""

	image_input = None
	storage = None
	image_main_result = None

	myV = 30
	otherV = 80

	notifyDistance = 100

	trackbarName = "my velocity"
	display_output_window_name = "Display Output"

	def __init__(self):
		self.cascade = cv2.CascadeClassifier()
		self.checkcascade = cv2.CascadeClassifier()
		self.load_cascade()

	def getImage(self, src):
		if src is None:
			print "src not filled"
			return
		self.image_input = src
		self.storage = src
		self.image_main_result = src

	def cascade_load(self, cascade_string):
		if self.cascade.load(cascade_string) is None:
			print "Could not load classifier cascade"

	def checkcascade_load(self, checkcascade_string):
		if self.checkcascade.load(checkcascade_string) is None:
			print "Could not load classifier cascade"

	def drawMarks(self, input_rectangles):
		input_rectangles = np.array(input_rectangles).tolist()
		input_rectangles, weights = cv2.groupRectangles(input_rectangles, 0, 100)
		for rect in input_rectangles:
			distance = calDistance(rect)
			if distance < self.notifyDistance:
				color = (0, 0, 255)
				self.drawExclamationMark(rect, color)
			else:
				if self.myV > self.otherV:
					color = (0, 0, 255)
					self.drawRectangle(rect, color)
					self.drawExclamationMark(rect, color)
				else:
					if self.myV == self.otherV and self.myV > distance / 2:
						color = (0, 0, 255)
						self.drawRectangle(rect, color)
						self.drawExclamationMark(rect, color)
					else:
						color = (0, 255, 0)
						self.drawRectangle(rect, color)

	def drawRectangle(self, rect, color):
		width = rect[2] / 40
		pt1 = (rect[0], rect[1])
		pt2 = (rect[0] + rect[2], rect[1] + rect[3])
		cv2.rectangle(self.image_main_result, pt1, pt2, color, width)

	def drawExclamationMark(self, rect, color):
		rect_center = (rect[0] + rect[2] / 2, rect[1] + rect[3] / 2)
		times = (rect[2] / 30, 0)[0]
		exclamationMarkUpper = [
			[-2 * times + rect_center[0], -7 * times + rect_center[1]],
			[-2 * times + rect_center[0], 2 * times + rect_center[1]],
			[2 * times + rect_center[0], 2 * times + rect_center[1]],
			[2 * times + rect_center[0], -7 * times + rect_center[1]]]
		exclamationMarkLower = [
			[-2 * times + rect_center[0], 3 * times + rect_center[1]],
			[-2 * times + rect_center[0], 7 * times + rect_center[1]],
			[2 * times + rect_center[0], 7 * times + rect_center[1]],
			[2 * times + rect_center[0], 3 * times + rect_center[1]]]
		exclamationMarkUpper = np.array(exclamationMarkUpper, np.int32)
		exclamationMarkLower = np.array(exclamationMarkLower, np.int32)

		cv2.fillPoly(self.image_main_result, [exclamationMarkUpper], color)
		cv2.fillPoly(self.image_main_result, [exclamationMarkLower], color)

	def onTrackbraChange(self, value):
		self.myV = value
		print "my V: " + str(self.myV)
		print "other V: " + str(self.otherV)

	def display_output(self):
		if self.image_main_result is None:
			return
		cv2.imshow(self.display_output_window_name, self.image_main_result)
		cv.CreateTrackbar(self.trackbarName, self.display_output_window_name,
		                  30, 200, self.onTrackbraChange)

	def findcars(self):
		img = self.storage
		if img is None:
			print "Image is empty."
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 3)
		resize_image = gray
		cars = self.cascade.detectMultiScale(resize_image, 1.1, 15, 0, (20, 30))
		input_rectangles = []
		for car in cars:
			car_x, car_y, car_w, car_h = car
			margin = 15
			resize_image_reg_of_interest = resize_image[
				car_y + margin:car_y + margin + car_h + margin,
				car_x + margin:car_x + margin + car_w + margin]
			nested_cars = self.checkcascade.detectMultiScale(
				resize_image_reg_of_interest,
				1.1, 1, 0, (5, 50))
			if len(nested_cars) > 0:
				input_rectangles.append(car)
				# cv2.imshow('roi', resize_image_reg_of_interest)
				# cv2.waitKey(0)
		self.drawMarks(input_rectangles)

	def load_cascade(self):
		self.checkcascade_load("./cascades/checkcas.xml")

		cascades = [
			"./cascades/cas1.xml",
			"./cascades/cas2.xml",
			"./cascades/cas3.xml",
			"./cascades/cas4.xml"]
		for cas in cascades:
			self.cascade_load(cas)


def calDistance(rect):
	width = rect[2]
	return 22726 * math.pow(width, -0.9776)


def videoCaptureWrap(file_name, callback):
	capture = cv2.VideoCapture(file_name)
	if capture.isOpened():
		while True:
			ret, image = capture.read()
			if image is None:
				break
			callback(image)
			if cv2.waitKey(1) & 0xff == ord('q'):
				break
	capture.release()
	cv2.destroyAllWindows()


def imageReadWrap(file_name, callback):
	image = cv2.imread(file_name)
	callback(image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()


def run_find_car(image):
	detectcars.getImage(image)
	detectcars.findcars()
	detectcars.display_output()

# main
detectcars = Cars()
input_file_name = sys.argv[1]
videoCaptureWrap(input_file_name, run_find_car)
imageReadWrap(input_file_name, run_find_car)
