__author__ = 'jeffreytang'

import cv2

cap = cv2.VideoCapture('data/test.avi')

fg_bg = cv2.createBackgroundSubtractorMOG2()

while cap.isOpened():
    success, frame = cap.read()
    if success:
        fg_mask = fg_bg.apply(frame)
        width, height = fg_mask.shape
        for i in range(width):
            for j in range(height):
                if not fg_mask[i, j]:
                    frame[i, j] = 0
        cv2.imshow('image', frame)
        k = cv2.waitKey(33)
        if k == 27:    # Esc key to stop
            break
    else:
        raise Exception('Cannot read the video / Done reading ...')
