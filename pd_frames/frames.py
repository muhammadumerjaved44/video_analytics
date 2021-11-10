# import some common libraries
import asyncio
import os

import cv2  # still used to save images out
from decord import VideoReader, cpu, gpu
# import local funciton here
from models import insert_frames


async def create_path(new_video_dir, frames_dir, video_name, frame_no):
    frame_name = f"image_{frame_no}.jpg"
    save_path = os.path.join(str(os.getcwd()),
                             new_video_dir,
                             frames_dir,
                             video_name,
                             frame_name)
    return save_path

async def save_image(save_path, frame):
    cv2.imwrite(save_path,
            cv2.cvtColor(
                frame.asnumpy(),
                cv2.COLOR_RGB2BGR)
            )


async def extract_frames(new_video_dir, video_path, frames_dir, overwrite=False, start=-1, end=-1, every=1):
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

    # make the paths OS (Windows) compatible
    video_path = os.path.normpath(video_path)
    # make the paths OS (Windows) compatible
    frames_dir = os.path.normpath(frames_dir)
    max_index = 0

    # get the video path and filename from the path
    video_dir, video_name = os.path.split(video_path)

    # can set to cpu or gpu .. ctx=gpu(0)
    vr = VideoReader(video_path, ctx=cpu(0))

    if start < 0:  # if start isn't specified lets assume 0
        start = 0
    if end < 0:  # if end isn't specified assume the end of the video
        end = len(vr)

    frames_list = list(range(start, end, every))
    saved_count = 0

    print("OKAY till here", len(frames_list), every)
    # this is faster for every > 25 frames and can fit in memory
    if every > 25 and len(frames_list) < 1000:
        frames = vr.get_batch(frames_list).asnumpy()
        special_index = 0

        # lets loop through the frames until the end
        for index, frame in zip(frames_list, frames):
            frame_no = str(special_index)

            # create async save path rutine call
            save_path = await asyncio.gather(
                    asyncio.create_task(create_path(new_video_dir, frames_dir, video_name, frame_no))
                    )
            save_path= save_path[0]

            # if it doesn't exist or we want to overwrite anyways
            if not os.path.exists(save_path) or overwrite:

                # insert into db
                results = {"frame_no": frame_no, "video_name": video_name, "file_path": save_path, 'is_processed': 0}

                await asyncio.gather(
                    asyncio.create_task(save_image(save_path, frame)),
                    asyncio.create_task(insert_frames(results))
                    )

                saved_count += 1  # increment our counter by one
                special_index = special_index+1
                max_index = special_index-1

            # call db save here
        return max_index
    else:
        # this is faster for every <25 and consumes small memory
        special_index = 0

        for index in range(start, end):  # lets loop through the frames until the end

            frame = vr[index]  # read an image from the capture
            # print(frame)

            if index % every == 0:  # if this is a frame we want to write out based on the 'every' argument
                frame_no = str(special_index)

                # create async save path rutine call
                save_path = await asyncio.gather(
                    asyncio.create_task(create_path(new_video_dir, frames_dir, video_name, frame_no))
                    )
                save_path= save_path[0]

                # if it doesn't exist or we want to overwrite anyways
                if not os.path.exists(save_path) or overwrite:
                    # print("Saving",save_path)

                    # save the extracted image

                    results = {"frame_no": frame_no, "video_name": video_name, "file_path": save_path, 'is_processed': 0}

                    await asyncio.gather(
                        asyncio.create_task(save_image(save_path, frame)),
                        asyncio.create_task(insert_frames(results))
                    )

                    saved_count += 1  # increment our counter by one
                    special_index = special_index+1
                    max_index = special_index-1

        return max_index  # and return the count of the images we saved


async def video_to_frames(video_path, frames_dir, overwrite=False, every=1):
    """
    Extracts the frames from a video
    :param video_path: path to the video
    :param frames_dir: directory to save the frames
    :param overwrite: overwrite frames if they exist?
    :param every: extract every this many frames
    :return: path to the directory where the frames were saved, or None if fails
    """

    # make the paths OS (Windows) compatible
    video_path = os.path.normpath(video_path)
    # make the paths OS (Windows) compatible
    frames_dir = os.path.normpath(frames_dir)
    # get the video path and filename from the path
    video_dir, video_name = os.path.split(video_path)
    new_video_dir = 'frame_dir'
    # make directory to save frames, its a sub dir in the frames_dir with the video name
    os.makedirs(os.path.join(new_video_dir, frames_dir, video_name), exist_ok=True)

    # let's now extract the frames
    saved_count = await extract_frames(new_video_dir, video_path, frames_dir, every=every)

    # os.path.join(frames_dir, video_name)  # when done return the directory containing the frames
    return saved_count


if __name__ == "__main__":
    video_path = 'video_download/file_example_MP4_1280_10MG.mp4.mp4'
    if not os.path.exists(video_path):
        raise FileNotFoundError(
            'file not found you need to pass the correct path')

    # video_to_frames(video_path, 'frames_folder', overwrite=False, every=1)
