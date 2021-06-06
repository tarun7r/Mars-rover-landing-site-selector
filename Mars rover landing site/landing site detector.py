
import cv2 as cv # OpenCV - real-time computer vision.
import numpy as np # To deal with high-level mathematical functions 
from PIL import Image, ImageTk  # image analysis and manipulating library
import tkinter as tk  # standard python GUI library
from essentials import Search, IMG_GRAY



app = Search('670x335 km')  # instantiate Search class and name it
app.run_rect_stats()  # call to run rect stats
app.draw_qc_rects()  # call draw qc rects
app.sort_stats()  # call sort stats
ptp_img = app.draw_filtered_rects(IMG_GRAY, app.ptp_filtered)  # create ptp sorted landing sites
std_img = app.draw_filtered_rects(IMG_GRAY, app.std_filtered)  # create std filtered landing sites

cv.imshow('Sorted by ptp for {} rect'.format(app.name), ptp_img)   # show window for ptp image
cv.waitKey(3000)  # wait 3 seconds
cv.imshow('Sorted std for {} rect'.format(app.name), std_img)  # show window for std image
cv.waitKey(3000)  # wait 3 seconds

app.make_final_display()  # Includes call to mainloop().  # create final display window
print('main succesful')


