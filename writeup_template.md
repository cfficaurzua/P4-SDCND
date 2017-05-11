

# **Advanced Lane Finding Project**

## Introduction

## Goals

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

[//]: # (Image References)

[image1]: ./examples/find_chess_board_example.PNG "Undistorted"
[image2]: ./examples/undistored_output.PNG "Road Transformed"
[image3]: ./examples/binary_combo_example.jpg "Binary Example"
[image4]: ./examples/warped_straight_lines.jpg "Warp Example"
[image5]: ./examples/color_fit_lines.jpg "Fit Visual"
[image6]: ./examples/example_output.jpg "Output"
[video1]: ./project_video.mp4 "Video"


## Camera Calibration

I build a function that get the object and image points from a set of images paths and a given number or rows and colums for the chessboard. at first it prepares the object poitns which is assumed to be fixed on the plane at z = 0, then it iterates throught the images looking for the real coordinates using the funcion provided by opencv to find chessboard patterns, next the aforementioned objecdt points and the recently discovered image points are appended each one to a correponsnding list which are both then returned by the function. 

Find chessboard corners in action:
![alt text][image1]

The output of the function was then used to compute the camera calibration and distortion coefficients using the cv2.calibrateCamera() function. the parameters were then saved in a file for later use. 
I constructed a simplified function of the cv2.undistort() function that only takes the image as a parameter.

The result can be seen below
![alt text][image2]

### Pipeline (single images)

Once the road images are correctly undistorted using the function as shown below:
![alt text][image2]

I proceed to change the perspective view to a bird eye view, in order to achieve this I create a pop up window that shows a picture of a straight road, then it retrieves the coordinates necessary to perfom the transformation, the user has to click the top corners of the lane from left to right following by the bottom left and right corners, a guide line is plotted above the image to help the user find the right coordinates.
The source points are then saved in a file for later use.

here you can see an example
![alt text][image2]

Then a function call get_perspective matrix, retrieve the corresponding perspective transform matrix and the inverse perspective transform matrix from the source points compute earlier and a a destination points which are fixed.

I then wrote a function called change_to-bird_eye, that used cv2.warpPerspective() function and change the image to a bird eye view using the transform matrix already computed and keeping the original image dimensions.

here it can be seen the bird eye transformation and later the backwards transformation.
![alt text][image2]

Next, in order to get a binary image containing only the lane lines i use a series of independent threshold system using horizontal and vertical sobel thresholding as well as the magnitude and direction thresholding as taught in the course, I also compute 
a second direction threshold using horizontal angles to substract the unwanted pixels from the images, I also use saturation channel from the hls colorspace, also the red and green channels were use as a filter and the l an b channels from the lab color space to enhance the white and yellow lines, all this functions were thresholded with a gauss fuzzy membership function, that outputs a range of certainty values instead of binary values, in addition a adaptiveThreshold provided by opencv and a custom horizontal convolution of the image was added for a more sturdy filter.

In order to obtain a final binary image, first all thresholded images were combined using the maximum instead of the logic *or* and the minimum instead of the logical *and*, so the red and green filter where mixed with the maximum function, as well as the l and b channels, and the pair of horizontal and vertical sobel, the minimum was used in the magnitude and direction threshold.
Then all results were sum up using corresponding weights of importance.
The final binary image was the result of evaluating all the pixels that were above .8 after applying all the filters.

All the threshold applied can be seen below
![alt text][image2]

to reduce unwanted noise a opening morphological operation was perform as shown below
![alt text][image2]

A line class was defined that contains information about if the line is detected, the x and y point for current frame, all the line parabola equation parameters up to ten frames, current line parabola equation parameters, the current line equation function and a image of the line.
the class also has two functions one for updating the parabola equation parameters, and another to get the proper equation parameters. 
the first function append the new parameters found. 
The other function gets the proper parameters using the median of all the coeficients stored.

Then two lines are inititialized, one for the left and another one for the right
To find each lane lines two windows of fix height are sliced from bottom to top of the image, the width of each varies increasing if nothing is found and shrinking if successfully found a lane, the windows width will never be greater than 150 pixels and smaller than 50 pixels. the middle point of the windows is calculated from the peak of a histogram of the window weighted so that the pixels farther from the center of the window are less important than the ones in the middle.

An additional function was constructed to find the lane lines from the parabola equation from a previous frame, to perform this the nonzero values of a region surrounding each line equation are taken into account for the new lane lines. 


the Fit_lines() function first extract the lines points using the find lane lines function explained before if there is no successfully detected lane in the previous frame, if not, it uses the additional function to extract the lane lines with the already known coefficients. 
Next it retrieves the coefficients using a polyfit function on nummpy.
Then it checks if the lane lines are more or less parallel by comparing the first coefficient of each line and if they have the proper distance between them comparing the second coefficient term.
if the lines are roughly parallel and properly separated, the new coefficients are appended to the history of coefficients of each line.

To compute the radius of curvature a new fitting function is 
coeficients compute the curvature of the radius given the formula in this [link]http://www.intmath.com/applications-differentiation/8-radius-curvature.php
the offset is calculated as the difference between the midpoint of the image and the midpoint between both line lanes at the bottom of the picture in bird eye view.

Then a lane is drawn using both fitted lines parabolas with the function cv2.fillPoly and 

#### 2. Describe how (and identify where in your code) you used color transforms, gradients or other methods to create a thresholded binary image.  Provide an example of a binary image result.

I used a combination of color and gradient thresholds to generate a binary image (thresholding steps at lines # through # in `another_file.py`).  Here's an example of my output for this step.  (note: this is not actually from one of the test images)

![alt text][image3]

#### 3. Describe how (and identify where in your code) you performed a perspective transform and provide an example of a transformed image.

The code for my perspective transform includes a function called `warper()`, which appears in lines 1 through 8 in the file `example.py` (output_images/examples/example.py) (or, for example, in the 3rd code cell of the IPython notebook).  The `warper()` function takes as inputs an image (`img`), as well as source (`src`) and destination (`dst`) points.  I chose the hardcode the source and destination points in the following manner:

```python
src = np.float32(
    [[(img_size[0] / 2) - 55, img_size[1] / 2 + 100],
    [((img_size[0] / 6) - 10), img_size[1]],
    [(img_size[0] * 5 / 6) + 60, img_size[1]],
    [(img_size[0] / 2 + 55), img_size[1] / 2 + 100]])
dst = np.float32(
    [[(img_size[0] / 4), 0],
    [(img_size[0] / 4), img_size[1]],
    [(img_size[0] * 3 / 4), img_size[1]],
    [(img_size[0] * 3 / 4), 0]])
```

This resulted in the following source and destination points:

| Source        | Destination   | 
|:-------------:|:-------------:| 
| 585, 460      | 320, 0        | 
| 203, 720      | 320, 720      |
| 1127, 720     | 960, 720      |
| 695, 460      | 960, 0        |

I verified that my perspective transform was working as expected by drawing the `src` and `dst` points onto a test image and its warped counterpart to verify that the lines appear parallel in the warped image.

![alt text][image4]

#### 4. Describe how (and identify where in your code) you identified lane-line pixels and fit their positions with a polynomial?

Then I did some other stuff and fit my lane lines with a 2nd order polynomial kinda like this:

![alt text][image5]

#### 5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

I did this in lines # through # in my code in `my_other_file.py`

#### 6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

I implemented this step in lines # through # in my code in `yet_another_file.py` in the function `map_lane()`.  Here is an example of my result on a test image:

![alt text][image6]

---

### Pipeline (video)

#### 1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

Here's a [link to my video result](./project_video.mp4)

---

### Discussion

#### 1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  
