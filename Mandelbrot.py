import numpy as np
import time
import pygame
import matplotlib.pyplot as plt
import math

#The recursive function to be used in generating the set
def generatingFunc(z, constant):
    return z**2 + constant

#Returns a string of time in minutes an seconds
def giveTime(start):
    now = time.time() - start
    minutes = int(now / 60)
    seconds = round(round(now) % 60)
    return str(minutes) + "' " + str(seconds) + '"'

#Height and length correspond to the pixel dimensions of the graph, which means it's also how many points will be analyzed in a column or row, respectively
def generatePoints(xMin, xMax, yMin, yMax, length, height, maxIt, growthFactor, screen):
    #img = Image.new('RGB', (length+1, height+1), color=0)
    start = time.time()

    y = yMin
    yCounter = 0
    while(y < yMax):
        print(str(round(100*(y-yMin)/(yMax-yMin),2)) + " percent done (y = " + str(round(y,2)) + ")")
        print("Time: " + giveTime(start))

        xCounter = 0
        x = xMin
        while(x < xMax):
            count = 0
            tempVal = 0
            testedVal = complex(x,y)

            #while(it's been too long or it's escaped the bounds)
            while(count < maxIt and abs(tempVal) < 2):
                tempVal = generatingFunc(tempVal, testedVal)
                count += 1
            color = int(pow(count,growthFactor) * 255 / pow(maxIt,growthFactor))
            if(count == maxIt): 
                #img.putpixel((xCounter,yCounter), (0,0,0))
                screen.set_at((xCounter, yCounter), (0,0,0))
            else:
                #img.putpixel((xCounter,yCounter), (int(color/1.3),color,int(color/1.3)))
                screen.set_at((xCounter, yCounter), (int(color/1.3),color,int(color/1.3)))
            x += (xMax-xMin) / (length)
            xCounter += 1

        y += (yMax-yMin) / (height)
        yCounter += 1

        pygame.display.flip()

    #img.show()
    #img.save("mandelbrot3.png","PNG")

#Takes 3 2d arrays of color values and combines them
def combineColors(r, g, b):
    r = r.astype(int)
    g = g.astype(int)
    b = b.astype(int)
    return np.dstack((r,g,b))

#Return a 3d array for the RGB values of the set
def toRGB(vals):
    maximum = np.amax(vals)
    ratio = 2 * (vals) / (maximum)
    b = 255*(1 - ratio)
    b[b < 0] = 0
    r = 255*(ratio - 1)
    r[r < 0] = 0
    g = 255 - b - r
    return combineColors(r, g, b)

def toGreen(vals):
    maximum = np.amax(vals)
    ratio = vals / maximum
    ratio[ratio == 1] = 0
    g = ratio * 255
    r = g / 1.3
    b = g / 1.3
    return combineColors(r, g, b)

def generatePointsNumpy(xRange, yRange, length, height, maxIt, growthFactor):
    x = np.linspace(xRange[0], xRange[1], length)
    y = np.linspace(yRange[0], yRange[1], height)
    isIn = np.full((length, height), True, dtype=bool)
    c = x[:,np.newaxis] + (1j * y[np.newaxis,:])
    mandelSet = np.zeros((length, height))
    z = np.copy(c)
    for i in range(maxIt):
        print(str(round(100 * i / maxIt)) + " percent done. Iteration " + str(i))
        z[isIn] = z[isIn]**2 + c[isIn]
        isIn[np.abs(z) > 2] = False
        mandelSet[isIn] = i
    mandelSet = np.power(mandelSet, growthFactor)
    mandelSet = toGreen(mandelSet)

    return mandelSet
    #plt.imshow(mandelSet)
    #plt.show()

#Returns the graph points from the mouse positions
def getPoints(xRange, yRange, rect, length, height, infoPanelHeight):
    topLeft = getPoint(xRange, yRange, rect.topleft, length, height, infoPanelHeight)
    bottomRight = getPoint(xRange, yRange, rect.bottomright, length, height, infoPanelHeight)
    if(topLeft[0] > bottomRight[0]): topLeft, bottomRight = bottomRight, topLeft
    return ((topLeft[0], bottomRight[0]), (topLeft[1], bottomRight[1]))

#Returns the graph point associated with the screen point
def getPoint(xRange, yRange, point, length, height, infoPanelHeight):
    if(point[1] < infoPanelHeight): point = (point[0], infoPanelHeight)
    xScale = (xRange[1] - xRange[0]) / length
    yScale = (yRange[1] - yRange[0]) / height
    return(xRange[0] + xScale * point[0], yRange[0] + yScale * (point[1]-infoPanelHeight))

#Returns a numpy rectangle object based on mouse coordinates.
#The initialPos is always correct, but the currentPos corner will be modified to keep the screen dimensions
#Does not allow you to go into the info panel
def getRect(initialPos, currentPos, screenRatio, infoPanelHeight):
    if(currentPos[1] < infoPanelHeight): currentPos = (currentPos[0], infoPanelHeight)
    tempHeight = currentPos[1] - initialPos[1]
    tempWidth = screenRatio * tempHeight
    return pygame.Rect(initialPos, (tempWidth,tempHeight))

def main():
    pygame.init()
    pygame.font.init()

    #Size of screen
    displayInfo = pygame.display.Info()
    infoPanelHeight = 100
    screenWidth = displayInfo.current_w
    screenHeight = displayInfo.current_h-100
    graphWidth = screenWidth
    graphHeight = screenHeight - infoPanelHeight
    graphRatio = graphWidth/graphHeight

    #Limits of graph
    minInitialXRange = (-2.25,1)
    minXLength = minInitialXRange[1] - minInitialXRange[0]
    minInitialYRange = (-1.25, 1.25)
    minYLength = minInitialYRange[1] - minInitialYRange[0]
    minRatio = minXLength / minYLength

    #Additional range needed to keep correct resolution
    xOffset = 0
    yOffset = 0
    if(minRatio > graphRatio):
        yOffset = ((1/graphRatio) * minXLength) - minYLength
    elif(minRatio < graphRatio):
        xOffset = (graphRatio * minYLength) - minXLength
    xRange = (minInitialXRange[0] - (xOffset/2), minInitialXRange[1] + (xOffset/2))
    yRange = (minInitialYRange[0] - (yOffset/2), minInitialYRange[1] + (yOffset/2))

    #Aesthetic
    growthFactor = 1/2
    maxIt = 200
    rectColor = (255,255,255)
    default_font = pygame.font.Font(pygame.font.get_default_font(), 15)
    decimal_count = 3

    screen = pygame.display.set_mode((screenWidth,screenHeight))

    #If a new mandelbrot image needs to be generated
    needToGenerate = False

    brotImage = pygame.surfarray.make_surface(generatePointsNumpy(xRange, yRange, graphWidth, graphHeight, maxIt, growthFactor))
    screen.blit(brotImage, (0,infoPanelHeight))
    screen.fill((255,255,255))
    #Position of where the mouse was held down, if at all
    mouseInitialPos = None
    # main loop
    running = True
    while running:

        if(needToGenerate):
            brotImage = pygame.surfarray.make_surface(generatePointsNumpy(xRange, yRange, graphWidth, graphHeight, maxIt, growthFactor))
            needToGenerate = False

        #Refresh background
        screen.fill((255,255,255))
        current_point = getPoint(xRange, yRange, pygame.mouse.get_pos(), graphWidth, graphHeight, infoPanelHeight)
        text_surface = default_font.render(f"Current point: {round(current_point[0], decimal_count)} + {round(current_point[1], decimal_count)}j", True, (0,0,0))
        screen.blit(text_surface, (0,0))
        screen.blit(brotImage, (0,infoPanelHeight))

        #The mouse is held down
        if(mouseInitialPos != None):
            tempPos = pygame.mouse.get_pos()
            pygame.draw.rect(screen, rectColor, getRect(mouseInitialPos, tempPos, graphRatio, infoPanelHeight), 2)
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            #Quit
            if(event.type == pygame.QUIT):
                running = False
            #Mouse events
            elif(event.type == pygame.MOUSEBUTTONDOWN):
                tempPos = event.pos
                if(tempPos[1] > infoPanelHeight):
                    mouseInitialPos = tempPos
            elif(event.type == pygame.MOUSEBUTTONUP):
                if(mouseInitialPos != None):
                    tempPos = pygame.mouse.get_pos()
                    #This will depend on the currest resolution of the points, so the whole program's stretching or shrinking will depend on the initial range of values
                    xRange, yRange = getPoints(xRange, yRange, getRect(mouseInitialPos, tempPos, graphRatio, infoPanelHeight), graphWidth, graphHeight, infoPanelHeight)
                    mouseInitialPos = None
                    needToGenerate = True

        pygame.display.flip()

main()
#generatePointsNumpy(-2, 1, -1, 1, 1000, 666, 50, 1/3, 1)
#generatePoints(-0.106548815638, -0.103527924525, -0.890801192967, -0.889310477469, 6000, 4000, 250, 1/2)
#generatePoints(-2, 1, -1, 1, 6000, 4000, 250, 1/3)