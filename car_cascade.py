import cv2
import numpy as np


class CarCascade(object):
	"""docstring for CarCascade"""
	def __init__(self):
		self.cascade = cv2.CascadeClassifier()
		self.checkcascade = cv2.CascadeClassifier()
		self.load_cascade()

	sourceImage = None
	outputImage = None

	output_rectangles = []

	def getImage(self, image):
		self.sourceImage = image
		self.initImageSize(image)

	def load_cascade(self):
		self.checkcascade_load("./cascades/checkcas.xml")

		cascades = ["./cascades/cas1.xml",
		            "./cascades/cas2.xml",
		            "./cascades/cas3.xml",
		            "./cascades/cas4.xml"]
		for cas in cascades:
			self.cascade_load(cas)

	def cascade_load(self, cascade_string):
		if self.cascade.load(cascade_string) is None:
			print "Could not load classifier cascade"

	def checkcascade_load(self, checkcascade_string):
		if self.checkcascade.load(checkcascade_string) is None:
			print "Could not load classifier cascade"

	def filterCars(self):
		if self.sourceImage is None:
			print "Image is empty."
		gray = cv2.cvtColor(self.sourceImage, cv2.COLOR_BGR2GRAY)
		treatedImg = treatImg(gray)
		cars = self.cascade.detectMultiScale(treatedImg, 1.1, 15, 0, (20, 30))
		self.output_rectangles = []
		for car in cars:
			car_x, car_y, car_w, car_h = car
			margin = 15
			treatedImgROI = treatedImg[car_y + margin:car_y + margin + car_h + margin,
			                           car_x + margin:car_x + margin + car_w + margin]
			nested_cars = self.checkcascade.detectMultiScale(treatedImgROI, 1.1, 1, 0, (5, 50))
			if len(nested_cars) > 0:
				self.output_rectangles.append(car)
		return self.output_rectangles

	def initImageSize(self, image):
		self.outputImage = np.zeros(image.shape, np.uint8)


def treatImg(image):
	image = cv2.GaussianBlur(image, (3, 3), 3)
	return image
