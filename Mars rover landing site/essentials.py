import cv2 as cv # OpenCV - real-time computer vision.
import numpy as np # To deal with high-level mathematical functions 
from PIL import Image, ImageTk  # image analysis and manipulating library
import tkinter as tk  # standard python GUI library

'''
what is mola and why should we use it instead of the normal images?
Data extracted from Nasa website (https://attic.gsfc.nasa.gov/mola/images.html)
The National Geographic Map of Mars was produced in a collaborative effort by the Mars Global Surveyor MOLA and MOC teams for the National Geographic Society.

It is an image of Mars that incorporates over 200 million laser altimeter measurements from MOLA and about a thousand wide-angle images from MOC. 
The altimetry accentuates details on the surface not visible in images due to the dusty atmosphere of Mars, and the image data provides realistic color. 
The image projection is Winkel-Tripel. (Image Credit: National Geographic Society, MOLA Science Team, MSS, JPL, NASA.)

'''

# loading the image in which we have to predict the potential landing sites
IMG_GRAY = cv.imread(r'C:\Users\tarun\Desktop\open\mars lander\mola_bandw.png', cv.IMREAD_GRAYSCALE)  # mola b&w image
IMG_COLOR = cv.imread(r'C:\Users\tarun\Desktop\open\mars lander\mola_color.png', cv.IMREAD_GRAYSCALE)  # mola color image


# constrains - Width,Height,Elevation and No_of_sites are variable | Mars circumfrence constant (21,344KM)
RECT_WIDTH_KM = 300  # limit size of rectangles
RECT_HT_KM  = 300     # limit size of rectangles
MAX_ELEV_LIMIT = 50   # elevation limit for landing site (km)
NUM_CANDIDATES = 20   # number of potential landing sites (variable) 
MARS_CIRCUM = 21344  # circumference of martian equator (21,344 KM)



# CONSTANTS: Derived:
IMG_HT, IMG_WIDTH = IMG_GRAY.shape  # height and width of the image
PIXELS_PER_KM = IMG_WIDTH / MARS_CIRCUM  # calculate pixels per km
RECT_WIDTH = int(PIXELS_PER_KM * RECT_WIDTH_KM)  # get size of rectangle
RECT_HT = int(PIXELS_PER_KM * RECT_HT_KM) # get height of rectangle
LAT_30_N = int(IMG_HT) // 3  # find 30 degrees N
LAT_30_S = LAT_30_N * 2 # find 30 degrees south
STEP_X = int(RECT_WIDTH / 2)  # amount to move search rectangle on x axis
STEP_y = int(RECT_HT / 2)  # amount to move search rectangle on the y axis

screen = tk.Tk()  # create screen object with tkinter
canvas = tk.Canvas(screen, width=IMG_WIDTH, height=IMG_HT + 130)  # create drawing area for graphics


class Search:

    def __init__(self, name):
        """initialise the search class"""
        self.name = name  # name of search object
        self.rect_coords = {}  # coordinates of rectangle corners
        self.rect_means = {}  # mean elevation of rectangle
        self.rect_ptps = {}  # peak to valley stats
        self.rect_stds = {}  # standard deviation stats
        self.ptp_filtered = []  # peak to peak filtered for lowest values
        self.std_filtered = []  # standard deviation filtered for lowest values
        self.high_graded_rects = []  # best landing sites

    def run_rect_stats(self):
        """Define rectangular search areas and calculate internal stats."""
        ul_x, ul_y = 0, LAT_30_N  # upper left corner of rectangle
        lr_x, lr_y = RECT_WIDTH, LAT_30_N + RECT_HT  # lower right corner of rectangle
        rect_num = 1  # number of rectangles

        while True:  # automate moving rectangles and recording their stats
            rect_img = IMG_GRAY[ul_y : lr_y, ul_x : lr_x]  # define the search area to the equatorial rectangle 30n - 30s
            self.rect_coords[rect_num] = [ul_x, ul_y, lr_x, lr_y]  # set corners of rectangle
            if np.mean(rect_img) <= MAX_ELEV_LIMIT:  # if search area is within elevation limit
                self.rect_means[rect_num] = np.mean(rect_img)  # record elevation average
                self.rect_ptps[rect_num] = np.ptp(rect_img)  # record peak to peak stats
                self.rect_stds[rect_num] = np.std(rect_img)  # record standard deviation stats
            rect_num += 1  # increase number of rectangles counter

            ul_x += STEP_X  # advance to next rectangle by 1 step
            lr_x = ul_x + RECT_WIDTH  # calculate corners
            if lr_x > IMG_WIDTH:  # if lower right corner is greater than image width
                ul_x = 0  # return to left side of image
                ul_y += STEP_y  # move 1 step on y axis
                lr_x = RECT_WIDTH  # get lower right corner
                lr_y += STEP_y  # set lower right y
            if lr_y > LAT_30_S + STEP_y:  # if you reach the bottom of the image
                break  # exit loop
        print("rect stats succesful")

    def draw_qc_rects(self):
        """Draw overlapping search rectangles on image as a check"""
        img_copy = IMG_GRAY.copy()  # create copy of gray img
        rects_sorted = sorted(self.rect_coords.items(), key=lambda x: x[0])  # sort list by numerical order
        print("\nRect Number and Corner Coordinates (ul_x, ul_y, lr_x, lr_y):")  # print rectangle coords
        for k, v in rects_sorted:  # for rectangle numbers and coords in sorted list
            print("rect: {}, coords: {}".format(k, v))  # print coords
            cv.rectangle(img_copy,  # draw rectangles on the img
                         (self.rect_coords[k][0], self.rect_coords[k][1]),
                         (self.rect_coords[k][2], self.rect_coords[k][3]),
                         (255, 0, 0), 1)  # rectangle corner coords, color, and line width
        cv.imshow('Qc Rects {}'.format(self.name), img_copy)  # show img with title
        cv.waitKey(3000)  # leave up for 3 seconds
        cv.destroyAllWindows()  # destroy the window
        print('qc rects succesful')

    def sort_stats(self):
        """Sort dictionaries by values and create lists of top N keys."""
        ptp_sorted = (sorted(self.rect_ptps.items(), key=lambda x: x[1]))  # create list of ptp sorted by value
        self.ptp_filtered = [x[0] for x in ptp_sorted[:NUM_CANDIDATES]]  # populate ptp filtered list with attributes
        std_sorted = (sorted(self.rect_stds.items(), key=lambda x: x[1]))  # sort std list by value
        self.std_filtered = [x[0] for x in std_sorted[:NUM_CANDIDATES]]  # populate std list with attributes
        for rect in self.std_filtered:  # for each rectangle search area in std filtered list
            if rect in self.ptp_filtered:  # if it also appears in ptp filtered list
                self.high_graded_rects.append(rect)  # add it to the high graded rects list
        print("sort stats complete")

    def draw_filtered_rects(self, image, filtered_rect_list):
        """Draw rectangles in list on image and return image."""
        img_copy = image.copy()  # create copy of image file
        for k in filtered_rect_list:  # for each filtered landing site result
            cv.rectangle(img_copy,
                         (self.rect_coords[k][0], self.rect_coords[k][1]),
                         (self.rect_coords[k][2], self.rect_coords[k][3]),
                         (255, 0, 0, ), 1)  # draw a white rectangle at coords
            cv.putText(img_copy, str(k),
                       (self.rect_coords[k][0] + 1, self.rect_coords[k][3] - 1),
                       cv.FONT_HERSHEY_PLAIN, 0.65, (255, 0, 0), 1)  # display name of landing site in the rectangle

        cv.putText(img_copy, '30 N', (10, LAT_30_N - 7),
                   cv.FONT_HERSHEY_PLAIN, 1, 255)  # draw title for 30 degrees north
        cv.line(img_copy, (0, LAT_30_N), (IMG_WIDTH, LAT_30_N),
                (255, 0, 0), 1)  # draw line for 30 degrees north
        cv.line(img_copy, (0, LAT_30_S), (IMG_WIDTH, LAT_30_S),
                (255, 0, 0), 1)  # draw title for 30 degrees south
        cv.putText(img_copy, '30 S', (10, LAT_30_S + 16),
                   cv.FONT_HERSHEY_PLAIN, 1, 255)  # draw line for 30 degrees south

        print('draw filtered rects succesful')
        return img_copy  # return image

    def make_final_display(self):
        """Use TK to show map of final rects & printout their statistics."""
        screen.title('Sites by MOLA Gray STD & PTP {} Rect'.format(self.name))  # set title of window

        img_color_rects = self.draw_filtered_rects(IMG_COLOR, self.high_graded_rects)
        # draw best landing sites on the color image

        img_converted = cv.cvtColor(img_color_rects, cv.COLOR_BGR2RGB)  # convert image to tkinter rgb
        img_converted = ImageTk.PhotoImage(Image.fromarray(img_converted))  # convert to tkinter photo image
        canvas.create_image(0, 0, image=img_converted, anchor=tk.NW)  # place image on canvas

        txt_x = 5  # x coord for text
        txt_y = IMG_HT + 20  # y coord for text
        for k in self.high_graded_rects:  # for landing sites in the list of best sites
            canvas.create_text(txt_x, txt_y, anchor='w', font=None,
                               text="rect={} mean elev={:.1f} std= {:.2f} ptp={}"
                               .format(k, self.rect_means[k], self.rect_stds[k],
                                       self.rect_ptps[k]))  # create statistics for landing site in info window
            txt_y += 15  # increment coord for y txt
            if txt_y >= int(canvas.cget('height')) - 10:  # if y txt is lower than bottom of rectangle
                txt_x += 300  # move x txt position
                txt_y = IMG_HT + 20  # move y txt position
        canvas.pack()  # optimize placement of objects
        screen.mainloop()  # run tkinter mainloop that display gui window and waits for key events
        print("make final display succesful")