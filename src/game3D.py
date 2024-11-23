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
    drawTrees(app)

def drawSky(app):
    drawRect(0, 0, app.width, app.height-kHorizonHeight, fill=kSkyGradient)

def drawMountains(app):
    drawImage(kMountainPath, app.width/2, app.height/2, width=app.width, height=app.height/1.2, align='center')

def drawClouds(app):
    app.clouds.sort(key=lambda cloud:cloud.scale)
    for cloud in app.clouds:
        drawImage(cloud.filePath, cloud.x, cloud.y, align='center', width=kCloudSize[0]*cloud.scale, height=kCloudSize[1]*cloud.scale)

def drawTrees(app):
    for tree in app.trees:
        drawTree(tree)

def drawTree(tree):
    pass

def drawGrass(app):
    offset = 40
    width = app.width + 2*offset
    height = app.height - kHorizonHeight
    now = time.time()
    drawRect(0, height, app.width, kHorizonHeight, fill=kBackgroundGradient0, opacity=100)
    drawRect(-offset+10*math.cos(.2*now), height, width, kHorizonHeight, fill=kBackgroundGradient2, opacity=30)
    drawRect(-offset+10*math.cos(.5*now), height, width, kHorizonHeight, fill=kBackgroundGradient3, opacity=30)
    drawRect(-offset+30*math.cos(.8*now), height, width, kHorizonHeight, fill=kBackgroundGradient4, opacity=30)

def drawFrisbees(app):
    for frisbee in app.frisbees:
        xPos = frisbee.y * app.width / app.height 
        yPos = app.height - frisbee.z*kFrisbeeHeightFactor - min(frisbee.x/app.width * kHorizonHeight, kHorizonHeight)
        sizeMultiplier = max(0.01, min(1, (2*(app.width-frisbee.x)/app.width+.1)))
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
    
def drawGame(app):
    drawBackground(app)
    drawFrisbees(app)