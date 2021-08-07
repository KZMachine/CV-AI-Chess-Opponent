import cv2 as cv
import numpy as np
import Board
from time import sleep
from settings import *

def takePicture(fileName):
    capture = cv.VideoCapture(0)

    ret, frame = capture.read()
     
    cv.imwrite(fileName + '.png', frame)

    image = cv.imread(fileName + '.png',cv.IMREAD_GRAYSCALE)
    #image = cv.imread(fileName + '.png',cv.IMREAD_COLOR)

    img = cv.flip(image, -1)
    cv.imwrite(fileName + '.png', image)
    #print(img)
    return img

def getPhysicalBoard():
    capture = cv.VideoCapture(0)

    ret, frame = capture.read()
     
    cv.imwrite('initialBoardView.png', frame)

    image = cv.imread('initialBoardView.png',0)
    img = cv.flip(image, -1)
    ret,binary = cv.threshold(img,105,255,cv.THRESH_TOZERO)


    cv.imwrite('Binary.png', binary)
        
    img = cv.imread('Binary.png',0)
    dst = cv.Canny(img,100,200)
    cv.imwrite('Canny.png', dst)

    cdst = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)
    cdstP = np.copy(cdst)

    linesP = cv.HoughLinesP(dst, 1, np.pi / 180, 50, 1, 15, 150)

    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv.LINE_AA)

    #cv.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdstP)

    physicalBoardGrid = []
    redRowValue = -1
    isRedRow = False
    isSameRow = False
    posY = []
    posX = []
    for i in range(0, len(cdstP)):
        pos = []
        secondRedLine = True
        
        red = -1
        numRedPixels = 0
        if isRedRow:
            if isSameRow:
                posY[len(posY)-1] = redRowValue
                isSameRow = False
            else:
                posY.append(redRowValue)
            isRedRow = False
                
        for j in range(len(cdstP[0])):
            if cdstP[i][j][2] == 255:
                if red > 0 and j-red > 25:
                    if secondRedLine:
                        pos.append(red)
                        secondRedLine = False
                    pos.append(j)
                red = j
                numRedPixels += 1
            elif numRedPixels > 100:
                isRedRow = True
                if i - redRowValue == 1:
                    isSameRow = True
                redRowValue = i
                break
        posX.append(pos)

    for i in posX:
        if len(i) == 9:
            physicalBoardGrid.append(i)
            break
    physicalBoardGrid.append(posY)

    print(physicalBoardGrid)
    cv.imwrite('HoughLines.png', cdstP)
    return physicalBoardGrid

def comparePositions(previousState, gridPosition, physicalBoardGrid):
    currentState = takePicture('currentState')
    pixelsChanged = 0
    totalPixels = 0
#     print(physicalBoardGrid)
    bias = 5
    for i in range(physicalBoardGrid[0][gridPosition[0]] + bias, physicalBoardGrid[0][gridPosition[0]+1] - bias):
        for j in range(physicalBoardGrid[1][gridPosition[1]] + bias, physicalBoardGrid[1][gridPosition[1]+1] - bias):
            if (abs(int(previousState[j][i]) - int(currentState[j][i])) > 10):
                pixelsChanged+=1
                cv.circle(currentState, (i,j), radius=0, color=(255,255,255),thickness=-1)
            totalPixels+=1
#             print(previousState[j][i], currentState[j][i])
    percentChanged = pixelsChanged/totalPixels
    print(percentChanged)
    
    cv.imwrite("changes.png", currentState)
    if(percentChanged > 0.2): #0.25
        return True
    return False
    
def playerMove(previousState, physicalBoardGrid):
    currentState = takePicture('currentState')
    gridPos = []
    percentImageChanged = []
    for x in range(0, 8):
        for y in range(0,8):
            pixelsChanged = 0
            totalPixels = 0
            bias = 0
            for i in range(physicalBoardGrid[0][x] + bias, physicalBoardGrid[0][x+1] - bias):
                for j in range(physicalBoardGrid[1][y] + bias, physicalBoardGrid[1][y+1] - bias):
                    if (abs(int(previousState[j][i]) - int(currentState[j][i])) > 10):
                        pixelsChanged+=1
                        cv.circle(currentState, (i,j), radius=0, color=(255,255,255),thickness=-1)
                    totalPixels+=1
        #             print(previousState[j][i], currentState[j][i])
            percentChanged = pixelsChanged/totalPixels
            #print(percentChanged)
            
            cv.imwrite("changes.png", currentState)
            if(percentChanged > 0.2): #0.25
                gridPos.append([x,y])
                percentImageChanged.append(percentChanged)
    gridPosFinal = []
    i = 0
    print(percentImageChanged)
    while i < len(percentImageChanged):
        if percentImageChanged[i] == max(percentImageChanged):
            gridPosFinal.append(gridPos[i])
            percentImageChanged[i] = 0
            i = 0
            if len(gridPosFinal) == 2:
                if gridPosFinal[0] != gridPosFinal[1]:
                    return gridPosFinal
        else:
            i+=1
    print(gridPosFinal)