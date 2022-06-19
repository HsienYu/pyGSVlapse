import cv2

from Panorama import Stitcher, Utils


def counter_clockwise_rotate(inputImage):
    output = cv2.transpose(inputImage)
    return cv2.flip(output, flipCode=0)


def clockwise_rotate(inputImage):
    output = cv2.transpose(inputImage)
    return cv2.flip(output, flipCode=1)


def main():
    p = [1, 2, 3, 4, 5, 6]
    print(p[:-3])
    return
    utils = Utils()

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


if __name__ == "__main__":
    main()
