import cv2
import time

def get_bg_mask(frame, bg_subtractor):
    """update bg_subtractor with new frame and return the updated mask"""
    bg_mask = bg_subtractor.apply(frame)
    return bg_mask

def subtract_bg(frame, bg_mask):
    """subtract bg from frame by setting each mask value to 0"""
    width, height = bg_mask.shape
    for i in range(width):
        for j in range(height):
            if not bg_mask[i, j]:
                frame[i, j] = 0
    return frame

def write_frame_and_bg(frame, bg_mask, name):
    """write frame and bg_mask to current directory with standardized format"""
    time_stamp = str(time.time())
    frame_file = open('_'.join(['frame', time_stamp, name]), 'w')
    mask_file = open('_'.join(['frame', time_stamp, name]), 'w')
    frame_file.write(frame)
    mask_file.write(bg_mask)
    frame_file.close()
    mask_file.close()

def main(video_file_path):
    """open video and return each frame and bg mask"""
    # get file name
    name = str(video_file_path.split('/')[-1])

    # open video
    cap = cv2.VideoCapture(video_file_path) 

    # instantiate bg subtractor
    bg_subtractor = cv2.BackgroundSubtractorMOG2()

    # read in each frame and save the frame and bg mask
    while cap.isOpened():
        success, frame = cap.read()
        if success:
            bg_mask = get_bg_mask(frame, bg_subtractor)
            write_frame_and_bg(frame, bg_mask, name)
        else:
            raise Exception('Cannot read the video / Done reading ...')

if __name__ == '__main__':
    main('test.avi')
