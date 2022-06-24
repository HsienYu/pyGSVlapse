import os
from os import path

from glob import glob
import cv2
from numpy import full, number

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


def getNineGridImagePath(rootFolder: str, frame: number, ext: str = 'jpg'):
    """
    0 1 2
    3 4 5
    6 7 8
    """
    definedPos = {
        0: 'left_top',
        1: 'center_top',
        2: 'right_top',
        3: 'left_middle',
        4: 'center_middle',
        5: 'right_middle',
        6: 'left_bottom',
        7: 'center_bottom',
        8: 'right_bottom',
    }

    if not rootFolder.endswith('/'):
        rootFolder = rootFolder + '/'

    result = []
    for key in definedPos:
        fullPath = '{folder}{pos}_{frame}.{ext}'.format(
            folder=rootFolder, pos=definedPos[key], frame=frame, ext=ext)
        if path.exists(fullPath):
            result.append(fullPath)

    return result


def stitchNineGridImage(input: list[str]):
    if len(input) != 9:
        return None

    images = []
    for path in input:
        images.append(cv2.imread(path))

    stitcher = Stitcher()
    top = stitcher.concatenateList(images[0:3])
    middle = stitcher.concatenateList(images[3:6])
    bottom = stitcher.concatenateList(images[6:9])
    # cv2.imwrite('./output/top.jpg', top)
    # cv2.imwrite('./output/middle.jpg', middle)
    # cv2.imwrite('./output/bottom.jpg', bottom)
    imgT = utils.clockwiseRotate(top)
    imgM = utils.clockwiseRotate(middle)
    imgB = utils.clockwiseRotate(bottom)
    result = stitcher.stitch([imgB, imgM])
    result = utils.autoCrop(result)
    result = stitcher.stitch([result, imgT])
    result = utils.autoCrop(result)
    result = utils.counterClockwiseRotate(result)

    return result


def stitchNineGridImage2(input: list[str]):
    imgs = []
    for i in range(len(input)):
        imgs.append(cv2.imread(input[i]))
    stitcher = Stitcher()
    top = stitcher.concatenateList(imgs[0:3])
    middle = stitcher.concatenateList(imgs[3:6])
    bottom = stitcher.concatenateList(imgs[6:9])
    imgT = utils.clockwiseRotate(top)
    imgM = utils.clockwiseRotate(middle)
    imgB = utils.clockwiseRotate(bottom)
    stitchy = cv2.Stitcher.create()
    (dummy, output) = stitchy.stitch([imgT, imgM, imgB])
    if dummy != cv2.STITCHER_OK:
        return None
    else:
        return utils.counterClockwiseRotate(output)


def main():
    pass
    # path = r'D:/GMap/tmp_outputs/'
    # nine = getNineGridImage(path, 0)
    # print(nine, len(nine))
    # img = stitchNineGridImage(nine)
    # cv2.imwrite('./output.jpg', img)


if __name__ == "__main__":
    main()
