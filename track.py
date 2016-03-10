import cv2
import numpy as np

def Tracking(center_child):
    camera_feed = cv2.VideoCapture(0)

    while(1):

        _,frame = camera_feed.read()
        #Convert the current frame to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        #Define the threshold for finding a blue object with hsv
        lower_blue = np.array([90,50,50])
        upper_blue = np.array([110,255,255])

        lower_pink = np.array([20,100,100])
        upper_pink = np.array([30,255, 255])


        #Create a binary image, where anything blue appears white and everything else is black
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
        mask_pink = cv2.inRange(hsv, lower_pink, upper_pink)
        #Get rid of background noise using erosion and fill in the holes using dilation and erode the final image on last time
        element = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
        mask_blue = cv2.erode(mask_blue,element, iterations=2)
        mask_blue = cv2.dilate(mask_blue,element,iterations=2)
        mask_blue = cv2.erode(mask_blue,element)

        mask_pink = cv2.erode(mask_pink,element, iterations=2)
        mask_pink = cv2.dilate(mask_pink,element,iterations=2)
        mask_pink = cv2.erode(mask_pink,element)
        
        mask = mask_blue + mask_pink
        #Create Contours for all blue objects
        imb, contoursb, hierarchyb = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        maximumAreab = 0
        bestContourb = None
        for contourb in contoursb:
            currentAreab = cv2.contourArea(contourb)
            if currentAreab > maximumAreab and currentAreab > 500:
                bestContourb = contourb
                maximumAreab = currentAreab

         #Create a bounding box around the biggest blue object
        if bestContourb is not None:
            x,y,w,h = cv2.boundingRect(bestContourb)
            cv2.rectangle(frame, (x,y),(x+w,y+h), (0,0,255), 3)

            # center = [x+w/2, y+h/2]
            # center_child.send(center)
            # q.put(arr)

        imp, contoursp, hierarchyp = cv2.findContours(mask_pink, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        maximumAreap = 0
        bestContourp = None
        for contourp in contoursp:
            currentAreap = cv2.contourArea(contourp)
            if currentAreap > maximumAreap and currentAreap > 500:
                bestContourp = contourp
                maximumAreap = currentAreap

         #Create a bounding box around the biggest blue object
        if bestContourp is not None:
            a,b,c,d = cv2.boundingRect(bestContourp)
            cv2.rectangle(frame, (a,b),(a+c,b+d), (0,0,255), 3)

        if bestContourb is not None and bestContourp is not None:

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

    print q.get()


    cv2.destroyAllWindows() 

if __name__ == '__main__':
    Tracking()