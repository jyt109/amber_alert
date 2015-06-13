import cv2
import time

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from aws_keys import get_aws_keys

def get_bg_mask(frame, bg_subtractor):
    """
    Produce mask using background subtractor

    :param frame: The image frame as numpy array
    :param bg_subtractor: OpenCV background subtractor class instance
    :return: mask as numpy array
    """
    mask = bg_subtractor.apply(frame)
    return mask

def subtract_bg(frame, mask):
    """
    Subtract mask from frame by setting each mask value to 0

    :param frame: Image frame as numpy array
    :param mask: Mask frame as numpy array
    :return: Image frame with background mask subtracted
    """
    width, height = mask.shape
    for i in range(width):
        for j in range(height):
            if not mask[i, j]:
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
    :return: Boolean
    """
    bound_box_frame, bound_box_mask = get_bounding_box(frame, mask)
    if bound_box_mask.mean() > .3 * 255.0:  # max value of mask pixel is 255
        return True
    else:
        return False

def write_frame_mask(frame, mask, name):
    """write frame and bg_mask to current directory with standardized format"""
    time_stamp = str(time.time())
    cv2.imwrite('_'.join(['frame', time_stamp, name])+'.png', frame)
    cv2.imwrite('_'.join(['mask', time_stamp, name])+'.png', mask)

def write_to_s3(frame, bg_mask, bucket, name):
    """create unique names and write files to S3 for import to Spark"""
    # get unique names for frame and bg_mask
    time_stamp = str(time.time())
    frame_name = '_'.join(['frame', time_stamp, name])+'.txt'
    bg_mask_name = '_'.join(['bgmask', time_stamp, name])+'.txt'

    # write frame to s3
    frame_s3 = Key(bucket)
    frame_s3.key = frame_name
    frame_s3.set_contents_from_string(frame.tostring())

    # write bg_mask to s3
    bg_mask_s3 = Key(bucket)
    bg_mask_s3.key = bg_mask_name
    bg_mask_s3.set_contents_from_string(frame.tostring())


def main(video_file_path):
    """open video and return each frame and bg mask"""
    # instantiate AWS bucket
    AWS_ACCESS, AWS_SECRET = get_aws_keys()
    conn = S3Connection(AWS_ACCESS, AWS_SECRET)
    bucket = conn.create_bucket('amber-alert-jyt109')

    # get file name
    #requires '/' path delimiting and a file name starting with '.'
    name = str(video_file_path.split('/')[-1].split('.')[0])

    # open video
    cap = cv2.VideoCapture(video_file_path) 

    # instantiate bg subtractor
    bg_subtractor = cv2.BackgroundSubtractorMOG2()

    # read in each frame and save the frame and bg mask
    while cap.isOpened():
        success, frame = cap.read()
        if success:
            bg_mask = get_bg_mask(frame, bg_subtractor)
            print "writing frame-mask combo to S3"
            write_to_s3(frame, bg_mask, bucket, name)
        else:
            raise Exception('Cannot read the video / Done reading ...')

if __name__ == '__main__':
    main('test.avi')
