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
    match key:
        case 'left':
            app.cameraX +=10
        case 'right':
            app.cameraX -= 10

def drawBackground(app):
    drawSky(app)
    drawMountains(app)
    drawClouds(app)
    drawGrass(app)

def drawSky(app):
    drawRect(0, 0, kAppWidth, kAppHeight-kHorizonHeight, fill=kSkyGradient)

def drawMountains(app):
    drawImage(kMountainPath, kAppWidth/2, (kAppHeight-kVerticalBuffer)/2.5, width=kAppWidth, height=(kAppHeight-kVerticalBuffer)-100, align='center')

def drawClouds(app):
    app.clouds.sort(key=lambda cloud:cloud.scale)
    for cloud in app.clouds:
        drawImage(cloud.filePath, cloud.x, cloud.y, align='center', width=kCloudSize[0]*cloud.scale, height=kCloudSize[1]*cloud.scale)

def getSizeMultiplier(app, xPos):
    return max(kMinSize, min(1, ((kAppWidth-(xPos-app.cameraX))/(kAppWidth))))

def drawScale(app):
    for i in range(0, (kAppHeight-kVerticalBuffer)//kZHeightFactor):
        drawLine(kAppWidth, i*kZHeightFactor, kAppWidth-10, i*kZHeightFactor)

def drawGrass(app):
    offset = 40
    width = kAppWidth + 2*offset
    height = (kAppHeight-kVerticalBuffer) - kHorizonHeight
    now = time.time()
    drawRect(0, height, kAppWidth, kHorizonHeight, fill=kBackgroundGradient0, opacity=100)
    drawRect(-offset+10*math.cos(.2*now), height, width, kHorizonHeight, fill=kBackgroundGradient2, opacity=30)
    drawRect(-offset+10*math.cos(.5*now), height, width, kHorizonHeight, fill=kBackgroundGradient3, opacity=30)
    drawRect(-offset+30*math.cos(.8*now), height, width, kHorizonHeight, fill=kBackgroundGradient4, opacity=30)

def drawFrisbees(app):
    for frisbee in app.frisbees:
        drawFrisbee(app, frisbee)

def drawFrisbee(app, frisbee):
    xPos = frisbee.y * (kAppWidth / (kAppHeight-kVerticalBuffer)) 
    yPos = (kAppHeight-kVerticalBuffer) - min((frisbee.x-app.cameraX)/kAppWidth * kHorizonHeight, kHorizonHeight) - frisbee.z*kZHeightFactor
    shadowY = yPos + frisbee.z*kZHeightFactor
    shadowX = xPos + frisbee.z*kZHeightFactor
    sizeMultiplier = getSizeMultiplier(app, xPos)

    width = kFrisbee3DSize
    height = max(abs(kFrisbee3DSize * math.sin(math.radians(frisbee.pitch))), 1)

    if frisbee.pitch >= 0:
        darkenBottom = False
        if abs(frisbee.roll) > 5: 
            fill = gradient('lightCyan', *[kFrisbeeColor]*int(60//abs(frisbee.roll)), 'skyBlue', 'steelBlue', start=('top' if frisbee.roll>0 else 'bottom'))
        else: fill = kDiscGradient
    else: 
        fill = kDiscGradient
        darkenBottom = True

    drawOval(xPos, yPos, width * sizeMultiplier, height * sizeMultiplier, rotateAngle=frisbee.roll, fill=fill, borderWidth=kDiscBorderWidth, border=kDiscGradient)
    drawOval(shadowX, shadowY, width * sizeMultiplier, height * sizeMultiplier, rotateAngle=frisbee.roll, fill='black', opacity=30)
    if darkenBottom: drawOval(xPos, yPos, width * sizeMultiplier, height * sizeMultiplier, rotateAngle=frisbee.roll, opacity=30, fill='black', borderWidth=kDiscBorderWidth, border='gray')


def drawCourse(app):
    minRenderingXPos = app.cameraX + kCameraRenderBuffer
    sizeMultiplier = getSizeMultiplier(app, app.course.goalPos.x)
    drawImage(kGoalPath, app.course.goal.y * (kAppWidth / (kAppHeight-kVerticalBuffer)), (kAppHeight-kVerticalBuffer) - min((app.course.goal.x-app.cameraX)/kAppWidth * kHorizonHeight, kHorizonHeight), align='bottom', width=50*sizeMultiplier*2, height=100*sizeMultiplier*2)
    for obstacle in reversed(app.course.obstacles):
        if obstacle.x < minRenderingXPos: continue
        sizeMultiplier = getSizeMultiplier(app, obstacle.x)
        match obstacle.type:
            case 'wall':
                drawWall(app, obstacle, sizeMultiplier)
            case 'tree':
                drawTree(app, obstacle, sizeMultiplier)
            case 'geyser':
                drawGeyser(app, obstacle, sizeMultiplier)
    drawFrisbees(app)

def drawGeyser(app, geyser, sizeMultiplier):
    width = geyser.width*sizeMultiplier*(kAppWidth / (kAppHeight-kVerticalBuffer))
    height = geyser.width/2 * sizeMultiplier
    centerX = geyser.y * (kAppWidth / (kAppHeight-kVerticalBuffer))
    bottomY = (kAppHeight-kVerticalBuffer) - min((geyser.x-app.cameraX)/kAppWidth * kHorizonHeight, kHorizonHeight)
    centerY = bottomY - height/2
    drawImage(kGeyserPath3D, centerX, centerY, align='center', width=width, height=height)
    if geyser.isActive:
        size = geyser.getSize(time.time())
        drawImage(kGeyserSpray3DPath, centerX, bottomY-5, align='bottom', width=size, height=2*size)

def drawWall(app, wall, sizeMultiplier):
    width = wall.width*sizeMultiplier*(kAppWidth / (kAppHeight-kVerticalBuffer))
    height = wall.height*sizeMultiplier*kZHeightFactor
    centerX = wall.y * (kAppWidth / (kAppHeight-kVerticalBuffer))
    # CENTER Y is the bottom point of the wall - half of the wall height
    bottomY = (kAppHeight-kVerticalBuffer) - min((wall.x-app.cameraX)/kAppWidth * kHorizonHeight, kHorizonHeight)
    centerY = bottomY - height/2
    if wall.isBouncy:
        fill=kBouncyColor
    else:
        fill='black'
    numHorizontalWalls = int(wall.width*(kAppWidth / (kAppHeight-kVerticalBuffer))/kWallImageWidth/kWallSizeMultiplier)
    numVerticalWalls = int(wall.height*kZHeightFactor/kWallImageHeight/kWallSizeMultiplier)
    for i in range(numVerticalWalls):
        for j in range(numHorizontalWalls):
            leftX = centerX - (width/2) + width/numHorizontalWalls*j
            topY = centerY - (height/2) + height/numVerticalWalls*i
            drawImage(wall.path3D, leftX, topY, width=width//numHorizontalWalls, height=height//numVerticalWalls, align='left-top')

def drawTree(app, tree, sizeMultiplier):
    width = 50*kTreeBaseSizeMultiplier * sizeMultiplier
    height = 100*kTreeBaseSizeMultiplier*sizeMultiplier
    xPos = tree.y * (kAppWidth / (kAppHeight-kVerticalBuffer))
    yPos = (kAppHeight-kVerticalBuffer) - min((tree.x-app.cameraX)/kAppWidth * kHorizonHeight, kHorizonHeight)
    drawImage(tree.path3D, xPos, yPos, align='bottom', width=width, height=height)

def drawThrowVisualization(app):
    drawFrisbee(app, Frisbee(\
                        (app.frisbeeInitPoint.tup()[0], app.frisbeeInitPoint.tup()[1], kFrisbeeThrowHeight),\
                        app.newFrisbee.direction,\
                        app.sliders2D[0].value(), \
                        app.sliders3D[1].value(), \
                        app.sliders3D[0].value(), \
                        app.sliders2D[1].value()))

def drawGame(app):
    drawBackground(app)
    drawCourse(app)
    if app.newFrisbee:
        drawThrowVisualization(app)
    drawScale(app)
