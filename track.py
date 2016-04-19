import cv2
import numpy as np

def create_mask(frame, lower, upper):
    """ Create mask for specified color threshold """
    #Convert the current frame to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # #Create a binary image, where anything blue and yellow appears white and everything else is black
    mask = cv2.inRange(hsv, lower, upper)
    #Get rid of background noise using erosion and fill in the holes using dilation and erode the final image on last time
    element = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    mask = cv2.erode(mask, element, iterations=2)
    mask = cv2.dilate(mask, element, iterations=2)
    mask = cv2.erode(mask, element)
    return mask

def find_object(frame, mask):
    """ Find colored objects"""
    # Create contours
    im, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    maximumArea = 0
    bestContour = None
    for contour in contours:
        currentArea = cv2.contourArea(contour)
        if currentArea > maximumArea and currentArea > 500:
            bestContour = contour
            maximumArea = currentArea

     #Create a bounding box around the biggest blue and yellow objects
    if bestContour is not None:
        x,y,w,h = cv2.boundingRect(bestContour)
        cv2.rectangle(frame, (x,y),(x+w,y+h), (0,0,255), 3)
        return x,y,w,h
    else:
        return None

def Tracking(center_child):
    """ Track colored objects and get their central positions"""
    camera_feed = cv2.VideoCapture(0)

    while(1):

        _,frame = camera_feed.read()

        #Define the threshold for finding blue and yellow objects with hsv
        lower_blue = np.array([90,50,50])
        upper_blue = np.array([110,255,255])

        lower_yellow = np.array([20,100,100])
        upper_yellow = np.array([30,255, 255])

        # create masks
        mask_blue = create_mask(frame,lower_blue, upper_blue)
        mask_yellow =create_mask(frame, lower_yellow, upper_yellow)        
        mask = mask_blue + mask_yellow
        
        #find biggest colored objects and get their positions
        blue = find_object(frame, mask_blue)
        yellow = find_object(frame, mask_yellow)
        if blue != None and yellow !=None :
            x,y,w,h = blue
            a,b,c,d = yellow
        # find the center of objects
            center = [a+c/2, b+d/2, x+w/2, y+h/2]
            center_child.send(center)

        #Show the original camera feed with a bounding box overlayed 
        cv2.imshow('frame',frame)
        #Show the contours in a seperate window
        cv2.imshow('mask',mask)
        #Use this command to prevent freezes in the feed
        k = cv2.waitKey(5) & 0xFF
        #If escape is pressed close all windows
        if k == 27:
            break

    cv2.destroyAllWindows() 

if __name__ == '__main__':
    Tracking()