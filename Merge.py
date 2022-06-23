from os import path
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
    definedPos = {
        'left_top': 0,
        'center_top': 1,
        'right_top': 2,
        'left_middle': 3,
        'center_middle': 4,
        'right_middle': 5,
        'left_bottom': 6,
        'center_bottom': 7,
        'right_bottom': 8
    }
    rootPath = r'E:/GMap/tmp_outputs/'
    files = glob(rootPath+'*_0.jpg', recursive=False)
    for f in files:
        pos = path.basename(f)
        pos = pos.removesuffix('_0.jpg')
        if pos in definedPos:
            print(definedPos[pos])
        else:
            print("Can not found {0}".format(pos))
    print(len(files))


def main():
    getNineGridImage(0)


if __name__ == "__main__":
    main()
