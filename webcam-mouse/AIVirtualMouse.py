import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy

wCam, hCam = 640, 480
frameR = 100     #Frame Reduction
smoothening = 10  #random value

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()

currentTime = time.time()
lastTime = time.time()
frameCount = 0
frameWithoutHandsCount = 0
currentFPS = 0

# print(wScr, hScr)

while True:
    # Step1: Find the landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    if cap.isOpened():
        frameCount+= 1
        currentTime = time.time()
        if len(lmList) == 0: frameWithoutHandsCount +=1
        if (currentTime - lastTime) >= 0.5:
            currentFPS = frameCount / (currentTime - lastTime)
            lastTime = currentTime
            frameCount = 0
        print('fps평균: ' + str(round(currentFPS)), end='\t')
        print('손없는프레임: ', str(frameWithoutHandsCount))
        if not success:
            print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
            continue
            #break
    
        cv2.putText(img, str(round(currentFPS)), (28, 58), cv2.FONT_HERSHEY_PLAIN, 3, (255, 8, 8), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(1)
    
        # Step2: Get the tip of the index and middle finger
        if len(lmList) != 0:
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]

            # Step3: Check which fingers are up
            fingers = detector.fingersUp()
            cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                        (255, 0, 255), 2)

            # Step4: Only Index Finger: Moving Mode
            if fingers[1] == 1 and fingers[2] == 0:

                # Step5: Convert the coordinates
                x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))

                # Step6: Smooth Values
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening

                # Step7: Move Mouse
                autopy.mouse.move(wScr - clocX, clocY)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY

            # Step8: Both Index and middle are up: Clicking Mode
            if fingers[1] == 1 and fingers[2] == 1:

                # Step9: Find distance between fingers
                length, img, lineInfo = detector.findDistance(8, 12, img)

                # Step10: Click mouse if distance short
                if length < 40:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                    autopy.mouse.click()

    # Step11: Frame rate

    # Step12: Display
    