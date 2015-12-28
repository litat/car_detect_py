import sys
import math
import cv2
import cv
import numpy as np


class Cars(object):
	"""docstring for Cars"""

	image_input = None
	storage = None
	image_main_result = None

	my_v = 30
	otherV = 80

	notifyDistance = 100

	myVTrackbarName = "My Velocity"
	notifyDistanceTrackbarName = "Notify Distance"
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
		input_rectangles, _ = cv2.groupRectangles(input_rectangles, 0, 100)
		for rect in input_rectangles:
			distance = calDistance(rect)
			if distance < self.notifyDistance:
				color = (0, 0, 255)
				self.drawExclamationMark(rect, color)
			elif self.my_v > self.otherV:
				color = (0, 0, 255)
				self.drawExclamationMark(rect, color)
			elif self.my_v > distance / 2:
				color = (0, 0, 255)
				self.drawExclamationMark(rect, color)
			else:
				color = (0, 255, 0)
				self.drawRectangle(rect, color)

	def drawRectangle(self, rect, color):
		height, width, channels = self.image_main_result.shape
		blank = np.zeros((height, width, channels), np.uint8)
		width = rect[2] / 40
		pt1 = (rect[0], rect[1])
		pt2 = (rect[0] + rect[2], rect[1] + rect[3])
		cv2.rectangle(blank, pt1, pt2, color, width)
		self.image_main_result = cv2.addWeighted(self.image_main_result, 1,
																						 blank, 0.5, 0)

	def drawExclamationMark(self, rect, color):
		height, width, channels = self.image_main_result.shape
		blank = np.zeros((height, width, channels), np.uint8)

		rect_center = (rect[0] + rect[2] / 2, rect[1] + rect[3] / 2)
		times = (rect[2] / 30, 0)[0]
		exclamationMarkUpper = [
			[-2 * times + rect_center[0], -8 * times + rect_center[1]],
			[-2 * times + rect_center[0], 1 * times + rect_center[1]],
			[2 * times + rect_center[0], 1 * times + rect_center[1]],
			[2 * times + rect_center[0], -8 * times + rect_center[1]]]
		exclamationMarkLower = [
			[-2 * times + rect_center[0], 3 * times + rect_center[1]],
			[-2 * times + rect_center[0], 7 * times + rect_center[1]],
			[2 * times + rect_center[0], 7 * times + rect_center[1]],
			[2 * times + rect_center[0], 3 * times + rect_center[1]]]
		exclamationMarkUpper = np.array(exclamationMarkUpper, np.int32)
		exclamationMarkLower = np.array(exclamationMarkLower, np.int32)

		cv2.fillPoly(blank, [exclamationMarkUpper], color)
		cv2.fillPoly(blank, [exclamationMarkLower], color)

		self.image_main_result = cv2.addWeighted(self.image_main_result, 1,
																						 blank, 100, 0)

	def whenMyVTrackbarChange(self, value):
		self.my_v = value

	def whenNotifyDistanceChange(self, value):
		self.notifyDistance = value

	def display_output(self):
		if self.image_main_result is None:
			return
		cv2.putText(self.image_main_result, "My Velocity: " + str(self.my_v),
								(0, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv.CV_AA)
		cv2.putText(self.image_main_result, "Other's Velocity: " + str(self.otherV),
								(0, 40), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv.CV_AA)
		cv2.putText(self.image_main_result,
								"Notify Distance: " + str(self.notifyDistance),
								(0, 60), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv.CV_AA)
		cv2.imshow(self.display_output_window_name, self.image_main_result)
		cv.CreateTrackbar(self.myVTrackbarName,
											self.display_output_window_name,
											self.my_v, 200, self.whenMyVTrackbarChange)
		cv.CreateTrackbar(self.notifyDistanceTrackbarName,
											self.display_output_window_name,
											self.notifyDistance, 100, self.whenNotifyDistanceChange)

	def findcars(self):
		img = self.storage
		if img is None:
			print "Image is empty."
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		treatedImg = treatImg(gray)
		cars = self.cascade.detectMultiScale(treatedImg, 1.1, 15, 0, (20, 30))
		input_rectangles = []
		for car in cars:
			car_x, car_y, car_w, car_h = car
			margin = 15
			treatedImgROI = treatedImg[
				car_y + margin:car_y + margin + car_h + margin,
				car_x + margin:car_x + margin + car_w + margin]
			nested_cars = self.checkcascade.detectMultiScale(
				treatedImgROI,
				1.1, 1, 0, (5, 50))
			if len(nested_cars) > 0:
				input_rectangles.append(car)
				# cv2.imshow('roi', treatedImgROI)
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


def treatImg(image):
	image = cv2.GaussianBlur(image, (3, 3), 3)
	return image


def calDistance(rect):
	width = rect[2]
	return 2272.6 * math.pow(width, -0.9776)


def videoCaptureWrap(file_name, callback):
	capture = cv2.VideoCapture(file_name)
	if capture.isOpened():
		while True:
			_, image = capture.read()
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
	DETECTCARS.getImage(image)
	DETECTCARS.findcars()
	DETECTCARS.display_output()

# main
DETECTCARS = Cars()
INPUT_FILE_NAME = sys.argv[1]
if "mp4" in INPUT_FILE_NAME:
	videoCaptureWrap(INPUT_FILE_NAME, run_find_car)
elif "jpg" in INPUT_FILE_NAME or "png" in INPUT_FILE_NAME:
	imageReadWrap(INPUT_FILE_NAME, run_find_car)
