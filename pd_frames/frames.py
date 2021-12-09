# import some common libraries
import asyncio
import os  # still used to save images out
from urllib.parse import urlparse

from decord import VideoReader, cpu  # , gpu # used when run on gpu
# import local funciton here
from models import insert_frames, update_progress_video_flag, upload_frames


async def extract_frames(video_path, video_id, overwrite=False, start=-1, end=-1, every=1):
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
    # video_path = os.path.normpath(video_path)
    # make the paths OS (Windows) compatible
    # frames_dir = os.path.normpath(frames_dir)
    max_index = 0

    # get the video path and filename from the path
    if video_path.startswith('http'):
        print('running from validators')
        video_name = urlparse(video_path).path.split('/')[-1]
    else:
        print('running not from validators')
        video_dir, video_name = os.path.split(video_path)
    print(video_name)
    # can set to cpu or gpu .. ctx=gpu(0)
    # with open(video_path, 'rb') as path:
    #     video_read = VideoReader(path, ctx=cpu(0))
    video_read = VideoReader(video_path, ctx=cpu(0))

    if start < 0:  # if start isn't specified lets assume 0
        start = 0
    if end < 0:  # if end isn't specified assume the end of the video
        end = len(video_read)

    frames_list = list(range(start, end, every))
    saved_count = 0

    print("OKAY till here", len(frames_list), every)
    # this is faster for every > 25 frames and can fit in memory
    if every > 25 and len(frames_list) < 1000:
        # creating error on batch execution if every > 25 frames
        # Need to run with cuda/GPU for a while
        # so that not to run this section
        # print('running from 25 frames')
        # frames = video_read.get_batch(frames_list).asnumpy()
        special_index = 0

        # lets loop through the frames until the end
        for index in frames_list:
            frame = video_read[index]
            frame_no = str(special_index)

            # if it doesn't exist or we want to overwrite anyways
            print('enter in loop')
            if not overwrite:
                print('enter in if not overwrite')

                # # insert into db
                save_path = await asyncio.gather(
                    asyncio.create_task(upload_frames(video_name, frame, frame_no))
                )

                results = {'video_id': video_id,
                           "frame_no": frame_no,
                           "video_name": video_name,
                           "file_path": save_path[0],
                           'is_processed': 0,
                           'is_ocr_processed':0,
                           }

                await asyncio.gather(
                    asyncio.create_task(insert_frames(results))
                    )

                saved_count += 1  # increment our counter by one
                special_index = special_index+1
                max_index = special_index-1

            # call db save here
        check_results = {'id': video_id,
                         'is_in_progress': 0,
                         'is_video_processed': 1,
                         }
        await asyncio.gather(
            asyncio.create_task(update_progress_video_flag(check_results))
            )
        return max_index
    else:
        # this is faster for every <25 and consumes small memory
        special_index = 0

        for index in range(start, end):  # lets loop through the frames until the end

            frame = video_read[index]  # read an image from the capture
            # print(frame)
            print('else loop')
            # if this is a frame we want to write out based on the 'every' argument
            if index % every == 0:
                frame_no = str(special_index)

                # if it doesn't exist or we want to overwrite anyways
                if not overwrite:
                    print('enter in else not overwrite')
                    print(video_name, frame, frame_no)
                    save_path = await asyncio.gather(
                        asyncio.create_task(upload_frames(video_name, frame, frame_no))
                    )
                    print(save_path)

                    results = {"video_id": video_id,
                               "frame_no": frame_no,
                               "video_name": video_name,
                               "file_path": save_path[0],
                               "is_processed": 0,
                               "is_ocr_processed":0,
                               }

                    print(results)
                    await asyncio.gather(
                        asyncio.create_task(insert_frames(results))
                        )

                    saved_count += 1  # increment our counter by one
                    special_index = special_index+1
                    max_index = special_index-1
        check_results = {'id': video_id, 'is_in_progress': 0, 'is_video_processed': 1}
        await asyncio.gather(
            asyncio.create_task(update_progress_video_flag(check_results))
            )
        return max_index  # and return the count of the images we saved


async def video_to_frames(video_path_url, video_id, overwrite=False, every=1):
    """
    Extracts the frames from a video
    :param video_path: path to the video
    :param frames_dir: directory to save the frames
    :param overwrite: overwrite frames if they exist?
    :param every: extract every this many frames
    :return: path to the directory where the frames were saved, or None if fails
    """

    # make the paths OS (Windows) compatible
    # video_path = os.path.normpath(video_path)
    # make the paths OS (Windows) compatible
    # frames_dir = os.path.normpath(frames_dir)
    # get the video path and filename from the path
    # video_dir, video_name = os.path.split(video_path)

    # make directory to save frames, its a sub dir in the frames_dir with the video name
    # os.makedirs(os.path.join(frames_dir, video_name), exist_ok=True)

    # let's now extract the frames
    saved_count = await extract_frames(video_path_url, video_id, overwrite=False, every=every)

    # os.path.join(frames_dir, video_name)  # when done return the directory containing the frames

    return saved_count


if __name__ == "__main__":
    VIDEO_PATH = 'http://192.168.20.200:9000/videos/file_example_MP4_1280_10MG.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=Q3AM3UQ867SPQQA43P2F%2F20211119%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20211119T122822Z&X-Amz-Expires=172800&X-Amz-SignedHeaders=host&X-Amz-Signature=588bd7d4a2b4937cc95c41935756850a6b0cc241a9fe666f44af7fa325f5d0bd'
    VIDEO_ID = 20
# if not os.path.exists(VIDEO_PATH):
#     raise FileNotFoundError(
#         'file not found you need to pass the correct path')
    # await video_to_frames(VIDEO_PATH, VIDEO_ID, overwrite=False, every=1)
