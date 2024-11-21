from constants import *
from cmu_graphics import *
import time, math
from classes import Frisbee, Vector3

kSkyGradient = gradient(*[kSkyDark, kSkyMedium, kSkyLight], start='bottom')

kBackgroundGradient0 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//80), start='left')
kBackgroundGradient1 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//80), start='center')
kBackgroundGradient2 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassDark, kGrassMedium]*(kAppWidth//200), start='top')
kBackgroundGradient3 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//150), start='left-top')
kBackgroundGradient4 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassDark, kGrassMedium]*(kAppWidth//300), start='right-top')

def drawBackground(app):
    drawSky(app)
    drawGrass(app)

def drawSky(app):
    drawRect(0, 0, app.width, app.height-kHorizonHeight, fill=kSkyGradient)
    drawClouds(app)

def drawClouds(app):
    for cloud in app.clouds:
        drawImage(cloud.filePath, cloud.x, cloud.y, align='center', width=kCloudSize[0]*cloud.scale, height=kCloudSize[1]*cloud.scale)

def drawGrass(app):
    offset = 40
    width = app.width + 2*offset
    height = app.height - kHorizonHeight
    now = time.time()
    drawRect(0, app.height, app.width, height, fill=kBackgroundGradient0)
    drawRect(-offset+10*math.cos(.2*now), height, width, kHorizonHeight, fill=kBackgroundGradient2, opacity=30)
    drawRect(-offset+10*math.cos(.5*now), height, width, kHorizonHeight, fill=kBackgroundGradient3, opacity=30)
    drawRect(-offset+30*math.cos(.8*now), height, width, kHorizonHeight, fill=kBackgroundGradient4, opacity=30)

def drawFrisbees(app):
    for frisbee in app.frisbees:
        xPos = frisbee.y * app.width / app.height 
        yPos = app.height - frisbee.z - min(frisbee.x/app.width * kHorizonHeight, kHorizonHeight)
        sizeMultiplier = max(0.01, min(1, (app.width/(frisbee.x)+.01)))
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