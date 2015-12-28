import sys
import cv2
import Cars


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
DETECTCARS = Cars.Cars()
INPUT_FILE_NAME = sys.argv[1]
if "mp4" in INPUT_FILE_NAME:
	videoCaptureWrap(INPUT_FILE_NAME, run_find_car)
elif "jpg" in INPUT_FILE_NAME or "png" in INPUT_FILE_NAME:
	imageReadWrap(INPUT_FILE_NAME, run_find_car)
