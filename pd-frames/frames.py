import os
# import some common libraries
import subprocess
import cv2  # still used to save images out
import numpy as np
from decord import VideoReader
from decord import cpu, gpu
from typing import Optional
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
# from Config import confignondatabase
# from decord.bridge import set_bridge
# set_bridge('torch')

def call_saved_to_db():
    pass

def extract_frames(video_path, frames_dir, overwrite=False, start=-1, end=-1, every=1):
    """
    Extract frames from a video using decord's VideoReader
    :param video_path: path of the video
    :param frames_dir: the directory to save the frames
    :param overwrite: to overwrite frames that already exist?
    :param start: start frame
    :param end: end frame
    :param every: frame spacing
    :return: count of images saved
    """
    # import os
    video_path = os.path.normpath(video_path)  # make the paths OS (Windows) compatible
    frames_dir = os.path.normpath(frames_dir)  # make the paths OS (Windows) compatible
    max_index=0
    video_dir, video_filename = os.path.split(video_path)  # get the video path and filename from the path

    # load the VideoReader
    vr = VideoReader(video_path, ctx=cpu(0))  # can set to cpu or gpu .. ctx=gpu(0)

    if start < 0:  # if start isn't specified lets assume 0
        start = 0
    if end < 0:  # if end isn't specified assume the end of the video
        end = len(vr)

    frames_list = list(range(start, end, every))
    saved_count = 0

    cwd = os.getcwd() #'D:\PointDuty\Project\MakeModelDetection\docker\JadeUI\jade_ui_pd\BackendDocker\PointDuty_API\PointDuty_API'#
    # print("cwd",cwd)
    print("OKAY till here",len(frames_list),every)
    if every > 25 and len(frames_list) < 1000:  # this is faster for every > 25 frames and can fit in memory
        frames = vr.get_batch(frames_list).asnumpy()
        special_index=0

        for index, frame in zip(frames_list, frames):  # lets loop through the frames until the end
            frame_name = "images_"+str(special_index)
            save_path = os.path.join(str(cwd),frames_dir, video_filename, frame_name+".jpg")  # create the save path
            # save_path=str(cwd)+"/"+frames_dir+"/"+str(video_filename)+"_images_"+str(special_index)+".png"
            if not os.path.exists(save_path) or overwrite:  # if it doesn't exist or we want to overwrite anyways
                # print("Saving",save_path)

                # cv2.imwrite(save_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))  # save the extracted image
                saved_count += 1  # increment our counter by one
                special_index=special_index+1
                max_index=special_index-1

                #call db save here
                # data = results.append({ "frame_no": frame_name, "video_frame": video_filename, 'frame_path': save_path })
        #         { "frame_no": "The Hobbit2", "video_frame": "Tolkien", 'frame_path': '/frame_rb' }
        # )
        
        # print(data)
        return max_index
    else:  # this is faster for every <25 and consumes small memory
        special_index=0
        results = []
        for index in range(start, end):  # lets loop through the frames until the end
            frame = vr[index]  # read an image from the capture
            # print(frame)
            # save_path=os.path.join(str(cwd),frames_dir, video_filename, "_images_"+str(special_index)+".jpg")
            if index % every == 0:  # if this is a frame we want to write out based on the 'every' argument
                frame_name = "images_"+str(special_index)
                save_path = os.path.join(str(cwd),frames_dir, video_filename, frame_name+".jpg")
                # save_path=os.path.join(str(cwd),frames_dir, video_filename, "_images_"+str(special_index)+".jpg")
                print({ "frame_no": frame_name, "video_frame": video_filename, 'frame_path': save_path })

                #save_path=str(frames_dir)+"\\"+str(video_filename)+"_images_"+str(special_index)+".png"
                if not os.path.exists(save_path) or overwrite:  # if it doesn't exist or we want to overwrite anyways
                    print("Saving",save_path)

                    cv2.imwrite(save_path, cv2.cvtColor(frame.asnumpy(), cv2.COLOR_RGB2BGR))  # save the extracted image
                    saved_count += 1  # increment our counter by one
                    special_index=special_index+1
                    max_index=special_index-1
            results.append({ "frame_no": frame_name, "video_frame": video_filename, 'frame_path': save_path })
        print(results)
        return max_index  # and return the count of the images we saved


def video_to_frames(video_path, frames_dir, overwrite=False, every=1):
    """
    Extracts the frames from a video
    :param video_path: path to the video
    :param frames_dir: directory to save the frames
    :param overwrite: overwrite frames if they exist?
    :param every: extract every this many frames
    :return: path to the directory where the frames were saved, or None if fails
    """

    video_path = os.path.normpath(video_path)  # make the paths OS (Windows) compatible
    frames_dir = os.path.normpath(frames_dir)  # make the paths OS (Windows) compatible
    video_dir, video_filename = os.path.split(video_path)  # get the video path and filename from the path

    # make directory to save frames, its a sub dir in the frames_dir with the video name
    os.makedirs(os.path.join(frames_dir, video_filename), exist_ok=True)

    #print("Extracting frames from {}".format(video_filename))

    saved_count=extract_frames(video_path, frames_dir, every=every)  # let's now extract the frames

    return saved_count #os.path.join(frames_dir, video_filename)  # when done return the directory containing the frames




if __name__ == "__main__":
    video_path = 'video_download/file_example_MP4_1280_10MG.mp4.mp4'
    if not os.path.exists(video_path):
        raise FileNotFoundError('file not found you need to pass the correct path')

    video_to_frames(video_path, 'frames_folder', overwrite=False, every=1)

