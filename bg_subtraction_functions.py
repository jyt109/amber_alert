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


def get_bounding_box(frame, mask, bounding_shape=(1000, 1200, 650, 800)):
    """
    This crops the frame and mask according to a bounding box that we have specified

    :param frame: The image frame that we are interested in
    :param mask: The background subtraction mask
    :param bounding_shape: The rectangular box in the image that we are interested in
    :return: bounding-box-frame, bounding-box-mask
    """

    x_min, x_max, y_min, y_max = bounding_shape
    bound_frame = frame[y_min:y_max, x_min:x_max]
    bound_mask = mask[y_min:y_max, x_min:x_max]
    return bound_frame, bound_mask


def discard_image_decision_rule(frame, mask):
    """
    Decision rule to decide if bounding-box-frame and bounding-box-mask should be kept.
    If car in bounding box, keep, else toss

    :param frame: bounding-box-frame (numpy.array)
    :param mask: bounding-box-mask (numpy.array)
    :return:
    """
    bound_box_frame, bound_box_mask = get_bounding_box(frame, mask)
    if bound_box_mask.mean() > .3 * 255.0:  # max value of mask pixel is 255
        return True
    else:
        return False

def write_frame_mask(frame, bg_mask, name):
    """write frame and bg_mask to current directory with standardized format"""
    time_stamp = str(time.time())
    cv2.imwrite('_'.join(['frame', time_stamp, name])+'.png', frame)
    cv2.imwrite('_'.join(['bgmask', time_stamp, name])+'.png', bg_mask)


def main(video_file_path):
    """open video and return each frame and bg mask"""
    # get file name
    #requires '/' path delimiting and a file name starting with '.'
    name = str(video_file_path.split('/')[-1].split('.')[0]) 

    # open video
    cap = cv2.VideoCapture(video_file_path) 

    # instantiate bg subtractor
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()

    # read in each frame and save the frame and bg mask
    while cap.isOpened():
        success, frame = cap.read()
        if success:
            bg_mask = get_bg_mask(frame, bg_subtractor)
            keep_bool = discard_image_decision_rule(frame, bg_mask)
            if keep_bool:
                print 'kept frame...'
                write_frame_mask(frame, bg_mask, name)
        else:
            raise Exception('Cannot read the video / Done reading ...')

if __name__ == '__main__':
    main('traffic_video.mov')
