import cv2
import numpy as np
import os
import glob
import pickle
import matplotlib.pyplot as plt
from tkinter import *
from PIL import Image,ImageTk

%matplotlib inline
patterns_path = 'camera_cal'
patterns_fn = glob.glob(os.path.join(os.getcwd(),patterns_path, 'calibration*.jpg'))

nx = 9
ny = 6

obj_points = []
img_points = []

objp = np.zeros((nx*ny,3), np.float32)
objp[:,:2] = np.mgrid[0:nx, 0:ny].T.reshape(-1,2)
for i, fn in enumerate(patterns_fn):

    img = cv2.imread(fn)
    #plt.imshow(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #plt.imshow(gray, cmap = 'gray')

    ret, corners = cv2.findChessboardCorners(gray, (nx, ny), None)
    if ret == True:
        print(i,i)
        # Draw and display the corners
        print(corners.shape)
        img_points.append(corners)
        obj_points.append(objp)
        #cv2.drawChessboardCorners(img, (nx, ny), corners, ret)
        #plt.imshow(img)
ret, mtx, dist, _, _  = cv2.calibrateCamera(obj_points, img_points, gray.shape[::-1],None,None)
calibration_param = dict([('mtx', mtx), ('dist', dist)])
pickle.dump(calibration_param, open('calibration_parameters.p', 'wb'))

test_image = cv2.imread(os.path.join(os.getcwd(), patterns_path, 'calibration2.jpg'))
plt.imshow(test_image)
undist = cv2.undistort(test_image, mtx, dist, None, mtx)
plt.imshow(undist)


test_images_path = 'test_images'
test_images_fn = glob.glob(os.path.join(os.getcwd(),test_images_path, '*.jpg'))

class SliderPopUp():
    def __init__(self, input_img):
        self.i = 0
        self.root = Tk()
        self.w1 = Scale(self.root, from_=0, to=255, orient=HORIZONTAL, length = 960, label = 'HL', command=self.update_img)
        self.w1.pack()
        self.w2 = Scale(self.root, from_=0, to=255, orient=HORIZONTAL, length = 960, label = 'HH', command=self.update_img)
        self.w2.pack()
        self.w3 = Scale(self.root, from_=0, to=255, orient=HORIZONTAL, length = 960, label = 'SL', command=self.update_img)
        self.w3.pack()
        self.w4 = Scale(self.root, from_=0, to=255, orient=HORIZONTAL, length = 960, label = 'SH', command=self.update_img)
        self.w4.pack()
        self.w5 = Scale(self.root, from_=0, to=255, orient=HORIZONTAL, length = 960, label = 'VL', command=self.update_img)
        self.w5.pack()
        self.w6 = Scale(self.root, from_=0, to=255, orient=HORIZONTAL, length = 960, label = 'VH', command=self.update_img)
        self.w6.pack()
        Button(self.root, text='save', command=self.save_values).pack()
        self.img = input_img
        self.panel1 = Label(self.root)
        self.panel1.pack(side ='left')
        self.panel2 = Label(self.root)
        self.panel2.pack(side ='left')
        self.panel3 = Label(self.root)
        self.panel3.pack()
        mainloop()

    def update_img(self, new_value):
        channel_1 = cv2.inRange(self.img[:,:,0], self.w1.get(), self.w2.get())
        channel_2 = cv2.inRange(self.img[:,:,1], self.w3.get(), self.w4.get())
        channel_3 = cv2.inRange(self.img[:,:,2], self.w5.get(), self.w6.get())
        image1 = ImageTk.PhotoImage(Image.fromarray(channel_1))
        image2 = ImageTk.PhotoImage(Image.fromarray(channel_2))
        image3 = ImageTk.PhotoImage(Image.fromarray(channel_3))
        self.panel1.configure(image = image1)
        self.panel1.image = image1
        self.panel2.configure(image = image2)
        self.panel2.image = image2
        self.panel3.configure(image = image3)
        self.panel3.image = image3
    def save_values(self):
        self.values = [self.w1.get(), self.w2.get(), self.w3.get(),self.w4.get(), self.w5.get(), self.w6.get()]
        self.root.destroy()
    def get_values(self):
        return self.values

def dir_threshold(img, sobel_kernel=3, thresh=(0, np.pi/2)):
    # Apply the following steps to img
    # 1) Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # 2) Take the gradient in x and y separately
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0,ksize = sobel_kernel)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1,ksize = sobel_kernel)
    # 3) Take the absolute value of the x and y gradients
    abs_x = np.absolute(sobelx)
    abs_y = np.absolute(sobely)
    # 4) Use np.arctan2(abs_sobely, abs_sobelx) to calculate the direction of the gradient
    orientation = np.arctan2(abs_y, abs_x)
    # 5) Create a binary mask where direction thresholds are met
    binary_output = np.zeros_like(orientation)
    # 6) Return this mask as your binary_output image
    binary_output[(orientation >= thresh[0]) & (orientation <= thresh[1])] = 1
    return binary_output


img = cv2.imread(os.path.join(os.getcwd(), test_images_path, 'test2.jpg'))
img = cv2.resize(img, None, fx=.25, fy= .25, interpolation =  cv2.INTER_AREA)

img.shape
a = SliderPopUp(cv2.cvtColor(img,cv2.COLOR_BGR2HLS))
a.get_values()
values = []
for i, fn in enumerate(test_images_fn):
    img = cv2.imread(fn)
    img = cv2.resize(img, None, fx=.25, fy= .25, interpolation =  cv2.INTER_AREA)
    undist_img = cv2.undistort(img, mtx, dist, None, mtx)

    HLS = cv2.cvtColor(undist_img, cv2.COLOR_BGR2HLS)
    a = SliderPopUp(cv2.cvtColor(undist_img,cv2.COLOR_BGR2HLS))
    a.get_values()
    values.append(a.get_values())
    del(a)
for i, fn in enumerate(test_images_fn):
    img = cv2.imread(fn)
    img = cv2.resize(img, None, fx=.25, fy= .25, interpolation =  cv2.INTER_AREA)
    undist_img = cv2.undistort(img, mtx, dist, None, mtx)
    rgb = cv2.cvtColor(undist_img, cv2.COLOR_BGR2RGB)
    HLS = cv2.cvtColor(undist_img, cv2.COLOR_BGR2HLS)
    H = HLS[:,:,0]
    L = HLS[:,:,1]
    S = HLS[:,:,2]

    plt.figure()
    plt.imshow(rgb)
    dir_thresh = dir_threshold(rgb,thresh= (0.9,1.0))
    plt.figure()
    plt.imshow(dir_thresh,cmap = 'gray')

    """
    plt.figure()
    plt.imshow(H,cmap = 'gray')
    H_thresh = cv2.adaptiveThreshold(H,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,101,2)
    plt.figure()
    plt.imshow(H_thresh,cmap = 'gray')

    plt.figure()
    plt.imshow(L,cmap = 'gray')
    L_thresh = cv2.adaptiveThreshold(L,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,101,2)
    plt.figure()
    plt.imshow(L_thresh,cmap = 'gray')

    plt.figure()
    plt.imshow(S,cmap = 'gray')
    S_thresh = cv2.adaptiveThreshold(S,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,501,2)
    plt.figure()
    plt.imshow(S_thresh,cmap = 'gray')"""

def change_to_bird_eye(input_img):
    h, w = input_img.shape[0], input_img.shape[1]
    src = np.float([[w,h],
                    [w,h],
                    [w,h],
                    [w,h]])
    dst = np.float([[w,h],
                    [w,h],
                    [w,h],
                    [w,h]])
    M = cv2.getPerspectiveTransform(src,dst)
    return cv2.warpPerspective(image, M, (w, h))
change_to_bird_eye(img)
