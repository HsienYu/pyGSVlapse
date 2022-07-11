from os import path

import cv2
from numpy import number

from Panorama import Stitcher, Utils

utils = Utils()


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
        output = utils.counterClockwiseRotate(output)
        output = utils.uniformSize(output)
        return output
