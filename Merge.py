from glob import glob
import cv2
from numpy import number

from Panorama import Stitcher, Utils

utils = Utils()


def test():
    output_file = './tmp/output.jpg'
    print("[INFO] loading images...")
    imgT = cv2.imread('./tmp/top.png')
    imgM = cv2.imread('./tmp/middle.png')
    imgB = cv2.imread('./tmp/bottom.png')

    stitcher = Stitcher()
    imgT = utils.clockwiseRotate(imgT)
    imgM = utils.clockwiseRotate(imgM)
    imgB = utils.clockwiseRotate(imgB)
    result = stitcher.stitch([imgB, imgM])
    result = utils.autoCrop(result)
    result = stitcher.stitch([result, imgT])
    result = utils.autoCrop(result)
    cv2.imwrite(output_file, utils.counterClockwiseRotate(result))


def getNineGridImage(frame: number):
    rootPath = 'D:/GMap/tmp_outputs'
    files = glob(rootPath, recursive=False)
    for f in files:
        print(f)
    print(len(files))


def main():
    getNineGridImage(0)


if __name__ == "__main__":
    main()
