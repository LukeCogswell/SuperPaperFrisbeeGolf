from constants import *
from cmu_graphics import *
import time, math
from classes import Frisbee, Vector2, Vector3

kSkyGradient = gradient(*[kSkyDark, kSkyMedium, kSkyLight], start='bottom')

kBackgroundGradient0 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//80), start='left')
kBackgroundGradient1 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//80), start='center')
kBackgroundGradient2 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassDark, kGrassMedium]*(kAppWidth//200), start='top')
kBackgroundGradient3 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//150), start='left-top')
kBackgroundGradient4 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassDark, kGrassMedium]*(kAppWidth//300), start='right-top')

def keyPressed(app, key):
    pass

def drawBackground(app):
    drawSky(app)
    drawMountains(app)
    drawClouds(app)
    drawGrass(app)
    drawWater(app)

def drawSky(app):
    drawRect(0, 0, kAppWidth, kAppHeight-kHorizonHeight, fill=kSkyGradient)

def drawMountains(app):
    drawImage(kMountainPath, kAppWidth/2, kAppHeight/2, width=kAppWidth, height=kAppHeight-100, align='center')

def drawClouds(app):
    app.clouds.sort(key=lambda cloud:cloud.scale)
    for cloud in app.clouds:
        drawImage(cloud.filePath, cloud.x, cloud.y, align='center', width=kCloudSize[0]*cloud.scale, height=kCloudSize[1]*cloud.scale)

def drawWater(app):
    pass

def getSizeMultiplier(app, xPos):
    return max(kMinSize, 2*min(1, ((kAppWidth-(xPos-app.cameraX))/kAppWidth)))

def drawScale(app):
    for i in range(0, kAppHeight//kZHeightFactor):
        drawLine(kAppWidth, i*kZHeightFactor, kAppWidth-10, i*kZHeightFactor)

def drawGrass(app):
    offset = 40
    width = kAppWidth + 2*offset
    height = kAppHeight - kHorizonHeight
    now = time.time()
    drawRect(0, height, kAppWidth, kHorizonHeight, fill=kBackgroundGradient0, opacity=100)
    drawRect(-offset+10*math.cos(.2*now), height, width, kHorizonHeight, fill=kBackgroundGradient2, opacity=30)
    drawRect(-offset+10*math.cos(.5*now), height, width, kHorizonHeight, fill=kBackgroundGradient3, opacity=30)
    drawRect(-offset+30*math.cos(.8*now), height, width, kHorizonHeight, fill=kBackgroundGradient4, opacity=30)

def drawFrisbees(app):
    for frisbee in app.frisbees:
        xPos = frisbee.y * (kAppWidth / kAppHeight) 
        yPos = kAppHeight - frisbee.z*kZHeightFactor - min((frisbee.x-app.cameraX)/kAppWidth * kHorizonHeight, kHorizonHeight)

        sizeMultiplier = getSizeMultiplier(app, xPos)

        width = kFrisbee3DSize
        height = max(kFrisbee3DSize * math.sin(math.radians(frisbee.pitch)), 1)

        if frisbee.pitch >= 0:
            darkenBottom = False
            if abs(frisbee.roll) > 5: 
                fill = gradient('lightCyan', *[kFrisbeeColor]*int(60//abs(frisbee.roll)), 'skyBlue', 'steelBlue', start=('top' if frisbee.roll>0 else 'bottom'))
            else: fill = kDiscGradient
        else: 
            fill = kDiscGradient
            darkenBottom = True

        drawOval(xPos, yPos, width * sizeMultiplier, height * sizeMultiplier, rotateAngle=frisbee.roll, fill=fill, borderWidth=kDiscBorderWidth, border=kDiscGradient)
        if darkenBottom: drawOval(xPos, yPos, width * sizeMultiplier, height * sizeMultiplier, rotateAngle=frisbee.roll, opacity=30, fill='black', borderWidth=kDiscBorderWidth, border='gray')
        if not frisbee.inFlight:
            drawLine(xPos, yPos-200, xPos, yPos, lineWidth=5, opacity=50, fill='red', arrowEnd=True)

def drawCourse(app):
    if app.frisbees != []:
        minRenderingXPos = app.frisbees[0].x
    else:
        minRenderingXPos = 0
    sizeMultiplier = getSizeMultiplier(app, app.course.goalPos.x)
    drawImage(kGoalPath, app.course.goal.y * (kAppWidth / kAppHeight), kAppHeight - min((app.course.goal.x-app.cameraX)/kAppWidth * kHorizonHeight, kHorizonHeight), align='bottom', width=50*sizeMultiplier, height=100*sizeMultiplier)
    for obstacle in reversed(app.course.obstacles):
        if obstacle.x < minRenderingXPos: continue
        sizeMultiplier = getSizeMultiplier(app, obstacle.x)
        match obstacle.type:
            case 'wall':
                centerX = obstacle.y * (kAppWidth / kAppHeight)
                centerY = kAppHeight-(obstacle.z*kZHeightFactor) - min((obstacle.x-app.cameraX)/kAppWidth * kHorizonHeight, kHorizonHeight)
                width = obstacle.width*sizeMultiplier*(kAppWidth / kAppHeight)
                height = obstacle.height*sizeMultiplier*kZHeightFactor
                if obstacle.isBouncy:
                    fill=kBouncyColor
                else:
                    fill='black'
                numHorizontalWalls = int(obstacle.width*(kAppWidth / kAppHeight)/kWallImageWidth/kWallSizeMultiplier)
                numVerticalWalls = int(obstacle.height*kZHeightFactor/kWallImageHeight/kWallSizeMultiplier)
                for i in range(numVerticalWalls):
                    for j in range(numHorizontalWalls):
                        leftX = centerX - (width/2) + width/numHorizontalWalls*j
                        topY = centerY - (height/2) + height/numVerticalWalls*i
                        drawImage(kWallPath, leftX, topY, width=width//numHorizontalWalls, height=height//numVerticalWalls, align='left-top')
            case 'tree':
                width = 50*kTreeBaseSizeMultiplier * sizeMultiplier
                height = 100*kTreeBaseSizeMultiplier*sizeMultiplier
                xPos = obstacle.y * (kAppWidth / kAppHeight)
                yPos = kAppHeight - min((obstacle.x-app.cameraX)/kAppWidth * kHorizonHeight, kHorizonHeight)
                drawImage(obstacle.path3D, xPos, yPos, align='bottom', width=width, height=height)
    drawFrisbees(app)

def drawGame(app):
    drawBackground(app)
    drawCourse(app)
    drawScale(app)
