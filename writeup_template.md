

# **Advanced Lane Finding Project**

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

[image1]: ./examples/find_chess_board_example.PNG "find_chess_board_example"
[image2]: ./examples/undistort_output.PNG "Road Transformed"
[image3]: ./examples/undistorted_road_image.PNG "Road Transformed"
[image4]: ./examples/pop_up_window.gif "pop_up_window"
[image5]: ./examples/bird_eye_view_transform.PNG "bird_eye_view_transform"
[image6]: ./examples/thresholding_example.PNG "thresholding example"
[image7]: ./examples/opening.PNG "Opening"
[image8]: ./examples/red_line_finding.PNG "Opening"
[image9]: ./examples/blue_line_finding.PNG "Opening"
[image10]: ./examples/fitted_curves.PNG "Opening"
[image11]: ./examples/output_picture.PNG "Opening"
[video1]: ./project_video.mp4 "Video"


## Camera Calibration

I build a function that get the object and image points from a set of images paths and a given number or rows and colums for the chessboard. at first it prepares the object poitns which is assumed to be fixed on the plane at z = 0, then it iterates throught the images looking for the real coordinates using the funcion provided by opencv to find chessboard patterns, next the aforementioned objecdt points and the recently discovered image points are appended each one to a correponsnding list which are both then returned by the function. 

Find chessboard corners in action

![alt text][image1]

The output of the function was then used to compute the camera calibration and distortion coefficients using the cv2.calibrateCamera() function. the parameters were then saved in a file for later use. 
I constructed a simplified function of the cv2.undistort() function that only takes the image as a parameter.

The result can be seen below

![alt text][image2]

### Pipeline (single images)

Once the road images are correctly undistorted using the function as shown below:

![alt text][image3]

I proceed to change the perspective view to a bird eye view, in order to achieve this I create a pop up window that shows a picture of a straight road, then it retrieves the coordinates necessary to perfom the transformation, the user has to click the top corners of the lane from left to right following by the bottom left and right corners, a guide line is plotted above the image to help the user find the right coordinates.
The source points are then saved in a file for later use.

here you can see an example

![alt text][image4]

Then a function call get_perspective matrix, retrieve the corresponding perspective transform matrix and the inverse perspective transform matrix from the source points compute earlier and a a destination points which are fixed.

I then wrote a function called change_to-bird_eye, that used cv2.warpPerspective() function and change the image to a bird eye view using the transform matrix already computed and keeping the original image dimensions.

here it can be seen the bird eye transformation and later the backwards transformation.

![alt text][image5]

Next, in order to get a binary image containing only the lane lines i use a series of independent threshold system using horizontal and vertical sobel thresholding as well as the magnitude and direction thresholding as taught in the course, I also compute 
a second direction threshold using horizontal angles to substract the unwanted pixels from the images, I also use saturation channel from the hls colorspace, also the red and green channels were use as a filter and the l an b channels from the lab color space to enhance the white and yellow lines, all this functions were thresholded with a gauss fuzzy membership function, that outputs a range of certainty values instead of binary values, in addition a adaptiveThreshold provided by opencv and a custom horizontal convolution of the image was added for a more sturdy filter.

In order to obtain a final binary image, first all thresholded images were combined using the maximum instead of the logic *or* and the minimum instead of the logical *and*, so the red and green filter where mixed with the maximum function, as well as the l and b channels, and the pair of horizontal and vertical sobel, the minimum was used in the magnitude and direction threshold.
Then all results were sum up using corresponding weights of importance.
The final binary image was the result of evaluating all the pixels that were above .8 after applying all the filters.

All the threshold applied can be seen below

![alt text][image6]

to reduce unwanted noise a opening morphological operation was perform as shown below

![alt text][image7]

A line class was defined that contains information about if the line is detected, the x and y points for the current frame, all the line's second order polynomial coefficients up to ten frames, the current line polynomial equation function and a image of the line.
the class also has two functions one for updating the parabola equation parameters, and another to get the proper equation parameters. 
the first function append the new coefficients found while the other function gets the proper coefficients using the median of all the coeficients stored.

Then two lines are inititialized, one for the left and another one for the right
To find each lane lines two windows of fix height are sliced from bottom to top of the image, the width of each window varies increasing if nothing is found and shrinking if successfully found a lane, the windows width will never be greater than 150 pixels and smaller than 50 pixels. the middle point of the windows is calculated from the peak of a histogram of the window weighted so that the pixels farther from the center of the window are less important than the ones in the middle.

here is an example of finding the right and left lane lines:

![alt text][image8]
![alt text][image9]

An additional function was constructed to find the lane lines from the parabola equation from a previous frame, to perform this the nonzero values of a region surrounding each line equation are taken into account for the new lane lines. 


the Fit_lines() function first extract the lines points using the find lane lines function explained before if there is no successfully detected lane in the previous frame, if not, it uses the additional function to extract the lane lines with the already known coefficients. 
Next it retrieves the coefficients using a polyfit function on nummpy.
Then it checks if the lane lines are more or less parallel by comparing the first coefficient of each line and if they have the proper distance between them comparing the second coefficient term.
If the lines are roughly parallel and properly separated, the new coefficients are appended to the history of coefficients of each line.

here are both fitted curves:

![alt text][image10]

To compute the radius of curvature the x and y values are multiply each with a corresponding factor to scale to real word dimension, in this case the x values were multiply by 3.7/700 m/px and the y values were multiply by 30/720 m/px.
Then new coefficients were obtained from the polyfit function embedded in numpy.
With the new coefficients the radius of curvater was calculated by the given the formula in this [link]http://www.intmath.com/applications-differentiation/8-radius-curvature.php

the offset is calculated as the difference between the midpoint of the image and the midpoint between both line lanes at the bottom of the picture in bird eye view.

Then a lane is drawn using both fitted lines parabolas with the function cv2.fillPoly over a black image then it was transform backwards to the original perspective using the inverse perspective matrix already obtained.
to blend the lane into the original picture the cv2.addWeighted function was used.
to overlay the lines a mask was created using the same function cv2.fillpoly and then transform as well to the original perspective. the pixels within the mask region were change with blue.

Then to add the corresponding text the cv2.putText function was used.

The final result for a picture can be seen below:

![alt text][image11]

## Pipeline (video)

To process a video, first both lines instances are initialized with default values, and then a function called proccess_video is called for each frame in which the following sequence is run:

1. undistort frame
2. change to bird eye view
3. obtain a combined binary image from thresholding process
4. apply opening morphological operation in order to denoise
5. run fit lines function
6. retrieve curvature and offset
7. draw result

Here's a [link the project video result](./video_output2.mp4)
Here's a [link the challenge video result](./video_output3.mp4)
Here's a [link the harder challenge video result](./video_output4.mp4)


## Discussion

First I thought that a fuzzy approach would be more robust than a binary one, but a lot of parameters needed to be tuned in order to correctly identify the lane lines in every situation, of course there are times that dazzing lights make really difficult spot the lines 
the same happens with too dark images. some times a reflection from the windshield obstruct the sight.
the algorithm made can highlight the lane lines most of the times. I came to notice that the gradients don't work in every situation because sometimes there are cracks on the roads that form lines very similar to the ones we are looking for, but the color discrimation can work alone as well, because the color can varies a lot from frame to frame, the saturation channel work pretty well in most of the situations, but in order to get the optimum result a combination of every tool we had was necessary.

when the algorithm fails to identify the lane lines is important to rely on the history we have to overcome any mistakes, and it is important to filter what we put in the history, so lanes that arent parallel or are too far apart shoulnd't be incorporated to our history, to prevent potentials errors.
The pipeline made in this project work well in the first video, but not so well as intended in the second and third video, but it could improve with more time spended, fixing some thresholding parameters, changing dynamically the bird eye view transformation, because in straight roads we could look ahead to a far distance, but when the roads have very closed turns, 
