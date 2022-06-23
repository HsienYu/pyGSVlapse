from turtle import width
from polyline.codec import PolylineCodec
# from moviepy.editor import *
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip, clips_array
import numpy as np
import reverse_geocoder as rg
import cv2
from Calculations import calculate_initial_compass_bearing, calculate_pitch
import urllib.parse
import json
import urllib.request
import urllib.error
import tempfile
import os
import shutil
import threading
import itertools
import time


# currentDir = os.getcwd()  # os.path.dirname(__file__)
currentDir = os.path.normpath(os.path.expanduser("D:/GMap"))
mediaDir = os.path.normpath(os.path.expanduser("D:/GMap"))
path_list = []
clip_list = []

_radius = 20


def set_GOOGLE_STREETVIEW_API_KEY(KEY):
    global GOOGLE_STREETVIEW_API_KEY
    GOOGLE_STREETVIEW_API_KEY = KEY

    global GOOGLE_MAPS_DIRECTIONS_API
    GOOGLE_MAPS_DIRECTIONS_API = "https://maps.googleapis.com/maps/api/directions/json?"

    global STREETVIEW_URL

    STREETVIEW_URL = (
        "http://maps.googleapis.com/maps/api/streetview?"
        "size=640x640&key=" + GOOGLE_STREETVIEW_API_KEY
    )


def _build_directions_url(origin, destination) -> str:
    query_paramaters = [
        ("origin", origin),
        ("destination", destination),
        ("key", GOOGLE_STREETVIEW_API_KEY),
    ]
    return GOOGLE_MAPS_DIRECTIONS_API + urllib.parse.urlencode(query_paramaters)


def get_result(url: str) -> "json":
    """parses the json"""
    response = None
    try:

        response = urllib.request.urlopen(url)
        json_text = response.read().decode(encoding="utf-8")

        return json.loads(json_text)

    finally:
        if response is not None:
            response.close()


def build_coords(json) -> list:
    # Builds coords from the polylines
    result = []
    for i in json["routes"][0]["legs"][0]["steps"]:
        result.extend(PolylineCodec().decode(i["polyline"]["points"]))
    return result


def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


def get_heading(start, end):
    return "{0:.4f}".format(calculate_initial_compass_bearing(start, end))


def removeDir(path):
    if os.path.exists(path):
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)
        else:
            shutil.rmtree(path)


class StreetViewThread(threading.Thread):
    def __init__(self, coordinates, pointindex, centercoord, height, driveby, position, pitch=0):
        threading.Thread.__init__(self)
        self.coordinates = coordinates
        self.pointindex = pointindex
        self.result = []
        self.driveby = driveby
        self.centercoord = centercoord
        self.height = height
        self.position = position
        self.pitch = pitch

    def run(self):
        for idx, coord in tuple(enumerate(self.coordinates))[:-3]:
            # -3 doesn't iterate through overlapping list. (for heading).
            # It looks 3 coords ahead for smoother change of view angle.
            # I lose 3 coords, tiny sacrifice.
            try:
                outfile = tempfile.NamedTemporaryFile(
                    delete=False, prefix=("{0:06}".format(self.pointindex + idx) + "__")
                )
                outfile.close()

                heading = get_heading(coord, self.coordinates[idx + 3])
                pitch = self.pitch  # -10 9
                pitch_shift = [-10, 9]
                fov = 40  # defualt 20 40
                fov_shift = [20, 40]
                fov_shift_index = 0  # tmp
                heading_shift = [-40, 0, 40]  # -20 0 20 # -40 0 40
                heading_shift_index = self.position

                url = "{}&location={},{}&fov={}&heading={}&pitch={}".format(
                    STREETVIEW_URL, coord[0], coord[1], fov, str(
                        float(heading) + heading_shift[heading_shift_index]), pitch
                )

                # coord,next_coord
                # Since I broke the coords list into chunks for different workers it can't look at the next coords at the end
                # of a single chunk. There has to be some overlap. So I added 3 from the next chunk into this chunk while
                # ending before the overlap.
                # [COORD1,COORD2,COORD3,COORD4,COORD5,COORD6],[COORD4,COORD5,COORD6,COORD7....]
                #                     ^Stops iterating here

                urllib.request.urlretrieve(url, outfile.name)
                self.result.append(outfile.name)

                print("{:.1%}".format(idx / len(self.coordinates)))
                print(url)
            except urllib.error.URLError:
                os.unlink(outfile.name)


def streetview_thread(coordinates, driveby="False", centercoord=(0, 0), height=0.0, position=0, pitch=0):
    # 20 is default number of threads "workers" unless the amount of images is less.
    NumberOfThreads = _radius
    NumberOfThreads = (
        len(coordinates) if len(
            coordinates) < NumberOfThreads else NumberOfThreads
    )
    slicedlist = [
        coordinates[i: i + (len(coordinates) // NumberOfThreads) + 3]
        for i in range(0, len(coordinates), len(coordinates) // NumberOfThreads)
    ]
    result_path = []
    threads = []
    for i in range(NumberOfThreads):
        t = StreetViewThread(
            slicedlist[i], (len(slicedlist[0]) * i),
            centercoord, height, driveby, position, pitch)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
        result_path.extend(t.result)
    return sorted(result_path, key=str)


def make_video(images, output_path, fps=30, size=(640, 640), is_color=True):
    """Makes video using xvid codec. Increase FPS for faster timelapse."""
    # fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    vid = cv2.VideoWriter(output_path, fourcc, fps, size, is_color)
    for image in images:
        img = cv2.imread(image)
        vid.write(img)
    vid.release()
    cv2.destroyAllWindows()


def save_location(local_list):
    # print(currentDir)
    outputlocation = []
    outputlocation.append(currentDir + "/tmp_outputs/")
    date_string = time.strftime("%Y-%m-%d-%H_%M_%S")
    location_string = (
        local_list[0] + '_' + local_list[1] + '-' + local_list[2] + '_' + local_list[3])
    date_location = date_string + '-' + location_string
    os.makedirs(mediaDir + "/StreetViewVideos/" + date_location, exist_ok=True)
    outputlocation.append(mediaDir + "/StreetViewVideos/" + date_location)
    # outputlocation = input("Where do you want to save this file?: \n")
    while not os.path.exists(outputlocation[0]):
        print("Invalid Path: " + outputlocation[0] + "\nTry again")
        outputlocation = input("Where do you want to save this file?: \n")
    return outputlocation


def make_stitchingVideo(path_List, save_path):
    # print(path_List)
    for i in range(0, len(path_List)):
        clip_list.append(VideoFileClip(path_List[i]))
    final_clip = clips_array([clip_list])
    final_clip.write_videofile(save_path + '/' + 'result.mp4')
    final_clip.close()
    clip_list.clear()
    #crop(x1=0, y1=0, x2=1920, y2=600)


def compare_frames(path_List):
    print("Checking amount of frames in each video")
    length_List = []
    for i in range(0, len(path_List)):
        cap = cv2.VideoCapture(path_List[i])
        property_id = int(cv2.CAP_PROP_FRAME_COUNT)
        length = int(cv2.VideoCapture.get(cap, property_id))
        length_List.append(length)
        # print(path_List[i] + ": " + str(length))

    # print(length_List)
    np_arr = np.array(length_List)
    comp = np.all(np_arr == np_arr[0])
    if comp:
        print("All videos are the same length")
        return True
    else:
        return False


def video_to_frames(video, path_output_dir):
    # extract frames from a video and save to directory as 'x.png' where
    # x is the frame index
    vidcap = cv2.VideoCapture(video)
    count = 0
    while vidcap.isOpened():
        success, image = vidcap.read()
        if success:
            cv2.imwrite(os.path.join(path_output_dir, '%d.png') %
                        count, image)
            count += 1
        else:
            break
    vidcap.release()
    cv2.destroyAllWindows()


def get_locationInfo(start, end):
    location_info = []
    start_info = rg.search(start)
    end_info = rg.search(end)
    location_info = [start_info[0]['cc'], start_info[0]
                     ['name'], end_info[0]['cc'], end_info[0]['name']]

    return location_info


def construct_images(START, END, NUM_THREADS):
    os.makedirs(os.path.join(currentDir, "tmp_outputs"), exist_ok=True)
    start = START
    end = END
    print("Generating a drive time-lapse")
    tmp_int = 0
    position_string = ['left', 'center', 'right']
    pitchs = [-17, 0, 16]
    for _ in itertools.repeat(None, 3):
        imageTops = streetview_thread(
            build_coords(get_result(_build_directions_url(start, end))), position=tmp_int, pitch=pitchs[2])
        imageMiddles = streetview_thread(
            build_coords(get_result(_build_directions_url(start, end))), position=tmp_int, pitch=pitchs[1])
        imageBottoms = streetview_thread(
            build_coords(get_result(_build_directions_url(start, end))), position=tmp_int, pitch=pitchs[0])
        # top
        idx = 0
        for image in imageTops:
            filename = '{0}/tmp_outputs/{1}_top_{2}.jpg'.format(
                currentDir, position_string[tmp_int], idx)
            output = cv2.imread(image)
            cv2.imwrite(filename, output)
            idx += 1
        # middle
        idx = 0
        for image in imageMiddles:
            filename = '{0}/tmp_outputs/{1}_middle_{2}.jpg'.format(
                currentDir, position_string[tmp_int], idx)
            output = cv2.imread(image)
            cv2.imwrite(filename, output)
            idx += 1
        # bottom
        idx = 0
        for image in imageBottoms:
            filename = '{0}/tmp_outputs/{1}_bottom_{2}.jpg'.format(
                currentDir, position_string[tmp_int], idx)
            output = cv2.imread(image)
            cv2.imwrite(filename, output)
            idx += 1

        tmp_int += 1
        if tmp_int == 3:
            print("done!")
            break


def construct_video(START, END, NUM_THREADS):
    # os.makedirs(currentDir + "/tmp_outputs", exist_ok=True)
    os.makedirs(os.path.join(currentDir, "tmp_outputs"), exist_ok=True)
    start = START  # input("Input Origin: ")
    end = END  # input("Input Destination: ")
    _radius = NUM_THREADS
    print("Generating a drive time-lapse")
    location_list = get_locationInfo(eval(start), eval(end))
    # location_list = ['jp', 'osaka', 'jp', 'tokyo']
    outputlocation = save_location(location_list)
    tmp_int = 0
    position_string = ['left', 'center', 'right']

    for _ in itertools.repeat(None, 3):
        # code iterates num times.
        # outputname = input("Please type in name of file: \n") + ".mp4"
        outputname = position_string[tmp_int] + ".mp4"
        path_list.append(currentDir + "/tmp_outputs/" + outputname)
        imagelocations = streetview_thread(
            build_coords(get_result(
                _build_directions_url(start, end))), position=tmp_int)

        # making video as mp4 format and change tmp_int
        make_video(imagelocations, os.path.join(
            outputlocation[0], outputname))
        tmp_int += 1
        print("StreetViewSliceVideo Generated Successfully at " +
              os.path.join(outputlocation[0], outputname))
        # print("path_list:" + str(path_list))
        if tmp_int == 3:
            if compare_frames(path_list):
                print("Stitching Video files")
                make_stitchingVideo(path_list, outputlocation[1])
                path_list.clear()
                video_to_frames(
                    outputlocation[1] + '/' + 'result.mp4', outputlocation[1])
                removeDir(currentDir + "/tmp_outputs")
                print("done!")
                break
            else:
                print("Video files are not the same length")
                print("Please fetching images again!")
                break
                # construct_video()
