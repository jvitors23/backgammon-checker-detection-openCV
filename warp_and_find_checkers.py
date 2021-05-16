import cv2
import numpy as np
import sys
import glob
import json
import os


def unwarp(img, board_coords):
    src = np.float32(board_coords)

    dst = np.float32([(0, 0),
                      (900, 0),
                      (900, 900),
                      (0, 900)])

    h, w = img.shape[:2]
    # use cv2.getPerspectiveTransform() to get M, the transform matrix
    M = cv2.getPerspectiveTransform(src, dst)

    # use cv2.warpPerspective() to warp your image to a top-down view
    warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_AREA)

    return warped[0:900, 0:900]


def locate_checkers(image, pip_size, checker_size, center_bar_size):
    # from https://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
    output = image.copy()
    image = cv2.medianBlur(image, 5)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    image_w = gray.shape[1]
    image_h = gray.shape[0]
    # detect circles in the image
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, checker_size/2-1,
                               param1=30, param2=20,
                               minRadius=int(checker_size/2 - 3), maxRadius=int(checker_size/2 + 2))

    output_json = {'top': [0 for i in range(12)],
                   'bottom': [0 for i in range(12)]}

    if circles is not None:

        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")

        r_mean = np.mean(circles[:, 2:])
        r_std = np.std(circles[:, 2:])

        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            if ((y < pip_size or y > image_h-pip_size) or (x > image_w/2 - 15 and x < image_w/2 + 15)):
                cv2.circle(output, (x, y), r, (0, 255, 0), 2)

                if y < pip_size:
                    if x < image_w/2:
                        for i in range(6):
                            if x > checker_size*i+10 and x < checker_size*(i+1)+10:
                                output_json['top'][i] += 1
                    else:
                        for i in range(6, 12):
                            if x > checker_size*i+center_bar_size+10 and x < checker_size*(i+1)+center_bar_size+10:
                                output_json['top'][i] += 1

                elif y > image_h-pip_size:
                    if x < image_w/2:
                        for i in range(6):
                            if x > checker_size*i+15 and x < checker_size*(i+1)+15:
                                output_json['bottom'][i] += 1

                    else:
                        for i in range(6, 12):
                            if x > checker_size*i+center_bar_size+15 and x < checker_size*(i+1)+center_bar_size+15:
                                output_json['bottom'][i] += 1
    return output, output_json


def apply_margin(board_coords, margin_x, margin_y, img_h, img_w):
    # add top left margin
    board_coords[0][0] = max(0, board_coords[0][0] - margin_x)
    board_coords[0][1] = max(0, board_coords[0][1] - margin_y)

    # add top right margin
    board_coords[1][0] = min(img_w, board_coords[1][0] + margin_x)
    board_coords[1][1] = max(0, board_coords[1][1] - margin_y)

    # add bottom right margin
    board_coords[2][0] = min(img_w, board_coords[2][0] + margin_x)
    board_coords[2][1] = min(img_h, board_coords[2][1] + margin_y)

    # add bottom left margin
    board_coords[3][0] = max(0, board_coords[3][0] - margin_x)
    board_coords[3][1] = min(img_h, board_coords[3][1] + margin_y)

    return board_coords


def main():
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    images = glob.glob(input_path+'/*.jpg')

    # margin added to the board coords
    margin_x = 40
    margin_y = 20

    for img_path in images:
        json_anot_file = open(img_path+'.info.json', 'r')
        img_annot = json.load(json_anot_file)
        img_annot = img_annot['canonical_board']

        original_img = cv2.imread(img_path)
        img_h, img_w, c = original_img.shape
        board_coords = img_annot['tl_tr_br_bl']

        # apply a margin to the board coords
        board_coords = apply_margin(
            board_coords, margin_x, margin_y, img_h, img_w)

        unwarped_image = unwarp(original_img, board_coords)
        
        pip_size = unwarped_image.shape[0] * \
            img_annot['pip_length_to_board_height']
        checker_size = pip_size/5
        center_bar_size = checker_size*img_annot['bar_width_to_checker_width']

        output_image, output_json = locate_checkers(
            unwarped_image, pip_size, checker_size, center_bar_size)

        if not os.path.exists(output_path):
            os.mkdir(output_path)

        output_filename = img_path.split('/')[-1].split('.')[0]

        cv2.imwrite(os.path.join(
            output_path, output_filename+'.visual_feedback.jpg'), output_image)

        with open(os.path.join(output_path, output_filename+'.jpg.checkers.json'), 'w') as output_json_file:
            json.dump(output_json, output_json_file)

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
