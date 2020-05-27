import numpy as np
import time
import pygame
import matplotlib.pyplot as plt
import math
from NumberInputBox import NumberInputBox

#The recursive function to be used in generating the set
def generatingFunc(z, constant):
    return z**2 + constant

#Returns a string of time in minutes an seconds
def giveTime(start):
    now = time.time() - start
    minutes = int(now / 60)
    seconds = round(round(now) % 60)
    return str(minutes) + "' " + str(seconds) + '"'

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

#Returns a 3d array for a heat map using the given RGB and values, with black values given to the maximum values
def toColor(vals, color):
    maximum = np.amax(vals)
    ratio = vals / maximum
    ratio[ratio == 1] = 0
    r, g, b = color
    r *= ratio
    g *= ratio
    b *= ratio
    return combineColors(r, g, b)

def generatePointsNumpy(xRange, yRange, length, height, maxIt, growthFactor, brot_color):
    x = np.linspace(xRange[0], xRange[1], length)
    y = np.linspace(yRange[0], yRange[1], height)
    isIn = np.full((length, height), True, dtype=bool)
    c = x[:,np.newaxis] + (1j * y[np.newaxis,:])
    mandelSet = np.zeros((length, height))
    z = np.copy(c)
    for i in range(maxIt):
        print(str(round(100 * i / maxIt)) + " percent done. Iteration " + str(i))
        z[isIn] = generatingFunc(z[isIn], c[isIn])
        isIn[np.abs(z) > 2] = False
        mandelSet[isIn] = i
    mandelSet = np.power(mandelSet, 1/growthFactor)
    mandelSet = toColor(mandelSet, brot_color)

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

#This will redraw (but not update) the screen
#Each drawing_list will be a list where drawing_list[0] is the start position, and the rest of the indecies are rows, with each row containing objects to blit
#NB: There do not need to be the same amount of columns in each row, and they don't have to have constant widths
def redraw_background(screen, color, *drawing_lists):
    screen.fill(color)
    for drawing_list in drawing_lists:
        current_pos = drawing_list[0]
        for i in range(1, len(drawing_list)):
            heights = []
            for j in drawing_list[i]:
                if(isinstance(j, NumberInputBox)): #TODO: Make interface
                    j.top_left = current_pos
                    temp_surface = j.get_surface()
                else:
                    temp_surface = j
                screen.blit(temp_surface, current_pos)
                current_pos = (current_pos[0] + temp_surface.get_width(), current_pos[1])
                heights.append(temp_surface.get_height())
            max_height = max(heights)
            current_pos = (drawing_list[0][0], current_pos[1] + max_height)

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
    growthFactor = 3
    maxIt = 200
    rectColor = (255,255,255)
    default_font = pygame.font.Font(pygame.font.get_default_font(), 15)
    decimal_count = 3
    brot_color = (255,0,100)

    #Tool objects
    growth_text = NumberInputBox((0,0), 50, 20, (200,200,200), default_font, str(growthFactor))

    #<---------------------------------------------------------------->

    screen = pygame.display.set_mode((screenWidth,screenHeight))

    #If a new mandelbrot image needs to be generated
    needToGenerate = False

    brotImage = pygame.surfarray.make_surface(generatePointsNumpy(xRange, yRange, graphWidth, graphHeight, maxIt, growth_text.get_factor(), brot_color))
    screen.blit(brotImage, (0,infoPanelHeight))
    screen.fill((255,255,255))
    #Position of where the mouse was held down, if at all
    mouseInitialPos = None


    # main loop
    #<---------------------------------------------------------------->
    running = True
    while running:

        if(needToGenerate):
            brotImage = pygame.surfarray.make_surface(generatePointsNumpy(xRange, yRange, graphWidth, graphHeight, maxIt, growth_text.get_factor(), brot_color))
            needToGenerate = False

        #Calculate and display the current position and range
        current_range = getPoints(xRange, yRange, pygame.Rect((0,infoPanelHeight),(graphWidth,graphHeight)),graphWidth,graphHeight,infoPanelHeight)
        current_range_surface = default_font.render(f"Current range: {round(current_range[0][0], decimal_count)} + {round(current_range[1][0], decimal_count)}j to {round(current_range[0][1], decimal_count)} + {round(current_range[1][1], decimal_count)}j", True, (0,0,0))
        current_point = getPoint(xRange, yRange, pygame.mouse.get_pos(), graphWidth, graphHeight, infoPanelHeight)
        current_surface = default_font.render(f"Current point: {round(current_point[0], decimal_count)} + {round(current_point[1], decimal_count)}j", True, (0,0,0))

        #Refresh background
        info_panel_drawing_list = [(0,0)]
        info_panel_drawing_list.append([current_range_surface])
        info_panel_drawing_list.append([current_surface])
        info_panel_drawing_list.append([default_font.render('Growth Factor: ', True, (0,0,0)), growth_text])

        mandel_drawing_list = [(0,infoPanelHeight)]
        mandel_drawing_list.append([brotImage])

        redraw_background(screen, (255,255,255), info_panel_drawing_list, mandel_drawing_list)

        #The mouse is held down
        if(mouseInitialPos != None):
            tempPos = pygame.mouse.get_pos()
            pygame.draw.rect(screen, rectColor, getRect(mouseInitialPos, tempPos, graphRatio, infoPanelHeight), 2)
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            growth_text.handle_event(event)
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
            #Key events
            elif(event.type == pygame.KEYDOWN):
                if(event.key == pygame.K_RETURN):
                    needToGenerate = True

        pygame.display.flip()

main()