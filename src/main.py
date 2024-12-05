from cmu_graphics import *
from constants import *
from classes import *
import game2D, game3D, math, time, os

def onAppStart(app):
    #DEFAULT SETTINGS
    app.width, app.height = kAppWidth, kAppHeight
    app.paused = kAppInitPauseState
    app.stepsPerSecond = kStepsPerSecond
    app.isTopDown = True
    app.showControls = False
    app.isStarting = True
    app.isTutorial = True
    app.isCourseOver = False
    app.tutorialStep = 0
    app.wind = Vector2(0,0)

    #Scoring
    app.holeScore = 0
    app.courseScore = 0
    app.currHole = 0

    # COURSE
    app.course = None
    resetCourse(app)
    app.scored = False
    app.cameraX = 0

    #Environment
    app.clouds = []
    app.trees = []
    app.windLines = []
    makeWindLines(app)

    #FRISBEE SETTINGS
    app.frisbees = []
    app.newFrisbee = None
    app.frisbeeInitPoint = Vector2(kFrisbeeSize*2, kAppHeight/2)
    app.upSpeed = 5
    app.initPitch = 10
    app.mousePos = None
    app.throwPoint = None
    app.curvePoint = None

    #SLIDERS
    app.sliders2D = [Slider('Power', *kPwrSettings), Slider('Roll', *kRollSettings)]
    app.sliders3D = [Slider('Pitch', *kPitchSettings), Slider('Up Power', *kUPPwrSettings)]
    app.isSliding = False
    app.sliderIndex = 0

    #PLAYER SETTINGS
    app.goalPos = Vector2(kAppWidth - kFrisbeeSize*2, kAppHeight/2)
    
    # DEBUG SETTINGS
    app.throwing = True
    app.settingPitch = False
    app.drawLabels = False

    #Splash Settings
    app.splashGeyser = Geyser(500, kAppHeight/2, kMinGeyserFrequency)
    app.splashGeyser.isActive = True
    app.splashGeyser.height = kMaxObstacleHeight * 4

def makeWindLines(app):
    for _ in range(kWindLineCount):
        x, y = random.random() * kAppWidth, random.random() * kAppHeight
        app.windLines.append(Vector2(x,y))

def onStep(app):
    if not app.paused:
        takeStep(app)

def takeStep(app):  
    for frisbee in app.frisbees:
        frisbee.takeFlightStep()
        # check if the frisbee is scored in the goal, if so add the hole's score to the total score
        if frisbee.checkScored(app.course.goal):
            frisbee.stop()
            app.scored = True
            app.courseScore += app.holeScore-app.course.calculatePar()
            app.frisbees = []
        else:
            # check for collisions with obstacles
            frisbee.checkCollisions(app.course)
            # if the frisbee is no longer in flight, check its position to make sure it landed in bounds
        if not frisbee.inFlight:
            # if the frisbee is out of bounds, reset the throwing position to the start of the course otherwise set the new frisbee throwing position to the frisbee's landing point
            if 0 > frisbee.x or frisbee.x > kAppWidth*(app.course.length//kMinCourseLength) or 0 > frisbee.y or frisbee.y > kAppHeight:
                frisbee.x = app.frisbeeInitPoint.x
                frisbee.y = app.frisbeeInitPoint.y
            else:
                app.frisbeeInitPoint = Vector2(frisbee.x, frisbee.y)
            #remove the frisbee from the game because it is no longer needed
            app.frisbees = []
        # update the camera x position for the 3d view for rendering
        if app.course:
            if frisbee.x < app.course.goal.x:
                app.cameraX = frisbee.x-kCameraRenderBuffer
            else:
                #always keep the goal in view
                app.cameraX = app.course.goal.x-kCameraRenderBuffer
    # update geysers
    for obstacle in app.course.obstacles:
        if obstacle.type == 'geyser':
            obstacle.checkActivation(time.time())
    # update clouds
    for cloud in app.clouds:
        cloud.move()
    #update wind lines
    for line in app.windLines:
        newX, newY = line.x + 10*app.wind.x, line.y + 10*app.wind.y
        newX %= kAppWidth
        newY %= kAppHeight
        line.x, line.y = newX, newY
    #spawn new clouds at a random height if the random int is 0 
    # (this makes cloud spawning irregular but should keep them spawning with a defined frequency)
    if not bool(random.randint(0, int(1 / kCloudFrequency))):
        path = (kOSFilePath+'/Images/Cloud'+str(random.randint(0, kCloudVariantCount-1))+'.png')
        newCloud = Cloud(path, random.randint(kMinCloudScale*10, kMaxCloudScale*10)/10)
        #only if the number of clouds on screen is low enough to we actually add a cloud
        if len(app.clouds) < kMaxCloudCount:
            app.clouds.append(newCloud)

# reset course settings and create a new one
def resetCourse(app):
    app.currHole += 1
    # if user has completed all {kMaxHoles} holes then display score on screen and prepare for a replay 
    if app.currHole > kMaxHoles:
        app.isCourseOver = True
        app.currHole = 1
    app.frisbees = []
    app.teams = [[],[]]
    app.course = None
    initCourse(app, random.randint(1, 3) * kMinCourseLength)
    app.frisbeeInitPoint = Vector2(kFrisbeeSize*2, kAppHeight/2)
    app.cameraX = 0
    app.scored=False
    app.holeScore = 0

def onKeyPress(app, key):
    #quit the application or the tutorial if ever clicked
    if key == 'escape':
        if app.isTutorial and not app.isStarting:
            app.isTutorial = False
        else:
            app.quit()
    #any key will advance the tutorial, exit the splash screen, or start a new course when the first one is over
    elif app.isStarting:
        app.isStarting = False
    elif app.isTutorial:
        advanceTutorial(app)
    elif app.isCourseOver:
        if key == 'space':
            app.isCourseOver = False
            app.isStarting = True
    elif app.scored:
        app.scored = False
        resetCourse(app)
    else:   
        match key:
            case 'space': # shoot the frisbee
                if app.frisbees == [] and (app.newFrisbee or (app.frisbeeInitPoint and app.throwPoint)):
                    if app.newFrisbee:
                        direction = app.newFrisbee.direction
                    else:
                        direction = app.throwPoint.subtracted(app.frisbeeInitPoint)
                    app.frisbees.append(
                        Frisbee(
                            (app.frisbeeInitPoint.tup()[0], app.frisbeeInitPoint.tup()[1], kFrisbeeThrowHeight),
                            direction,
                            app.sliders2D[0].value(), 
                            app.sliders3D[1].value(), 
                            app.sliders3D[0].value(),
                            app.sliders2D[1].value())) # pos, direction, forwardSpeed, upSpeed, pitch, roll
                    app.frisbees[-1].wind = app.wind
                    app.newFrisbee = None
                    app.holeScore += 1
                    WhooshSounds[random.randint(0, kWhooshes-1)].play()
                    if len(app.frisbees) > 1:
                        app.frisbees.pop(0)
            case 's': # debug keystroke
                takeStep(app)
            case 'c': # show controls for ingame help
                app.showControls = not app.showControls
            case 'r': # reset your throws in case you end up in a really bad position - tradeoff is it adds one to your throw count (no abusing this!)
                app.frisbeeInitPoint = Vector2(*kFrisbeeInitPos)
                app.frisbees = []
                app.holeScore += 1
                app.cameraX = 0
            case 'n': # debug keystroke for finding new courses
                resetCourse(app)
            case 't': # play tutorial again
                app.isTutorial = True
            case 'l': # debug keystroke to show details for objects
                app.drawLabels = not app.drawLabels
            case 'tab': # swap view
                app.isTopDown = not app.isTopDown
            case 'up' | 'right':
                if app.course:
                    app.cameraX += 10
                    if app.cameraX > kAppWidth*(app.course.length//kMinCourseLength-1): app.cameraX = kAppWidth*(app.course.length//kMinCourseLength-1)
            case 'down' | 'left':
                app.cameraX -= 10
                if app.cameraX < 0: app.cameraX = 0
            case _: # check perspective specific keystrokes - currently none active
                pass
                # if app.isTopDown:
                #     game2D.keyPressed(app, key)
                # else:
                #     game3D.keyPressed(app, key)
            # case 'n': # debug frisbee for flight patterns
            #     app.frisbees.append(Frisbee((200,200,0), Vector2(1,1), 50, 15, 20, 45))
            # case 'backspace': # debug remove a frisbee
            #     if app.frisbees != []:
            #         app.frisbees.pop(0)

def onKeyHold(app, keys):
    if not (app.isStarting or app.isCourseOver):
        if ('down' in keys or 'left' in keys) and not ('up' in keys or 'right' in keys):
            app.cameraX -= 30
            if app.cameraX < 0: app.cameraX = 0
        elif not ('down' in keys or 'left' in keys) and ('up' in keys or 'right' in keys):
            if app.course:
                app.cameraX += 30
                if app.cameraX > kAppWidth*(app.course.length//kMinCourseLength-1): app.cameraX = kAppWidth*(app.course.length//kMinCourseLength-1)
        
def advanceTutorial(app):
    app.tutorialStep += 1
    if app.tutorialStep >= kTutorialSteps:
        app.isTutorial = False
        app.tutorialStep = 0

def onMousePress(app, mouseX, mouseY):
    if not app.isStarting:
        if clickedInSlider1(mouseX, mouseY):
            app.isSliding = True
            app.sliderIndex = 0
        elif clickedInSlider2(mouseX, mouseY):
            app.isSliding = True
            app.sliderIndex = 1
        else:
            app.isSliding = False
            if app.throwing:
                if app.isTopDown:
                    app.throwPoint = Vector2(mouseX+app.cameraX, mouseY)
                    aimVector = app.throwPoint.subtracted(app.frisbeeInitPoint).unitVector()
                    roll = app.sliders2D[1].value()
                    newFrisbee = Frisbee((*app.frisbeeInitPoint.tup(), kFrisbeeThrowHeight), aimVector.unitVector(), aimVector.magnitude() * kAimControlMultiplier, app.upSpeed, app.initPitch, roll)
                    app.newFrisbee=newFrisbee

def onMouseMove(app, mouseX, mouseY):
    app.mousePos = Vector2(mouseX, mouseY)

def clickedInSlider1(x, y):
    return kAppWidth - 2*kSliderSpacing - kSliderWidth > x > kAppWidth - 2*kSliderSpacing - 2*kSliderWidth and kAppHeight-kSliderSpacing > y > kAppHeight-kSliderSpacing-kSliderHeight

def clickedInSlider2(x, y):
    return kAppWidth-kSliderSpacing > x > kAppWidth-kSliderSpacing-kSliderWidth and kAppHeight-kSliderSpacing > y > kAppHeight-kSliderSpacing-kSliderHeight

def initCourse(app, length):
    app.wind = Vector2((random.random()-.5) * 10, (random.random()-.5) * 10)
    app.course = Course(length, kDefaultObstaclePeriod, app.wind)
    addObstacles(app.course)

def addObstacles(course):
    if course.obstacles != []: return
    ## RANDOM OBSTACLE POSITIONS, HEIGHTS, TYPES, ETC ##
    for i in range(course.numObstacles):
        x = (i+1) * course.obstaclePeriod
        y = random.random() * (kAppHeight - 2*kSideBuffer) + kSideBuffer
        height = random.randint(0, kMaxObstacleHeight)
        obstacleChoice = random.choice(kObstacleTypes)
        match obstacleChoice:
            case 'wall':
                z = 0
                width = random.choice([i*kWallSizeMultiplier*kWallImageWidth/(kAppWidth / (kAppHeight-kVerticalBuffer)) for i in range(1,4)])
                height = random.choice([i*kWallSizeMultiplier*kWallImageHeight/kZHeightFactor for i in range(1,5)])
                newObstacle = Wall(x, y, z, width, height, random.choice([True, False, False]))
            case 'tree':
                newObstacle = Tree(x,y, kTreeHeight)
            case 'geyser':
                newObstacle = Geyser(x, y, random.random() * (kMaxGeyserFrequencey-kMinGeyserFrequency) + kMinGeyserFrequency)
            case _:
                raise SillyException(f'Silly Goof! {obstacleChoice} is not in the match cases!')
        course.obstacles.append(newObstacle)
    
## SLIDER CONTROL ## 
def onMouseDrag(app, mouseX, mouseY):
    if app.isSliding:
        relativeMouseHeight = (mouseY-kSliderSpacing-(kAppHeight-kSliderSpacing-kSliderHeight)) / kSliderHeight
        if app.isTopDown:
            app.sliders2D[app.sliderIndex].percentage = max(0, min(1-relativeMouseHeight, 1))
        else:
            app.sliders3D[app.sliderIndex].percentage = max(0, min(1-relativeMouseHeight, 1))

def drawFPS(app, timeStart):
    now = time.time()
    if now == timeStart:
        fps = 'Unlimited'
    else: 
        fps = int(1 / (now - timeStart))
    drawLabel(fps, kAppWidth, 0, align='right-top')

def drawSliders(slider1, slider2):
    yPos = kAppHeight - kSliderSpacing

    #slider 1
    xPos = kAppWidth - 2*kSliderWidth - 2*kSliderSpacing
    fill1 = game2D.getColorForPercentage(slider1.percentage)
    drawRect(xPos, yPos, kSliderWidth, kSliderHeight*max(0.001, slider1.percentage), align='left-bottom', opacity=kSliderOpacity, fill=fill1)
    drawRect(xPos, yPos, kSliderWidth, kSliderHeight, opacity=kSliderOpacity, border='black', borderWidth=kSliderBorderWidth, fill=None, align='left-bottom')
    xPos += kSliderWidth/2
    if slider1.label == 'Power':
        drawLabel(f'{int(100*slider1.percentage)}%', xPos, yPos-kSliderTextSize, size=kSliderTextSize)
    else:
        drawLabel(int(slider1.value()), xPos, yPos-kSliderTextSize, size=kSliderTextSize)
    drawLabel(slider1.label, xPos, yPos+kSliderTextSize/2, size=kSliderTextSize)


    #slider 2
    xPos = kAppWidth - kSliderWidth - kSliderSpacing
    fill2 = game2D.getColorForPercentage(slider2.percentage)
    drawRect(xPos, yPos, kSliderWidth, kSliderHeight*max(0.001, slider2.percentage), align='left-bottom', opacity=kSliderOpacity, fill=fill2)
    drawRect(xPos, yPos, kSliderWidth, kSliderHeight, opacity=kSliderOpacity, border='black', borderWidth=kSliderBorderWidth, align='left-bottom', fill=None)
    xPos += kSliderWidth/2
    drawLabel(int(slider2.value()), xPos, yPos-kSliderTextSize, size=kSliderTextSize)
    drawLabel(slider2.label, xPos, yPos+kSliderTextSize, size=kSliderTextSize)

def drawGameOver(app):
    drawRect(0, 0, kAppWidth, kAppHeight, fill=kTutorialColor)
    drawBorder(0, 0, kAppWidth, kAppHeight, 10)
    drawLabel(f'Congrats on completing {kMaxHoles} holes!', kAppWidth/2, kAppHeight/3, size=75, fill=kTutorialTextColor)
    drawLabel(f'Your score was: {app.courseScore}', kAppWidth/2, kAppHeight/2, size=75, fill=kTutorialTextColor)
    drawLabel(f"To play another {kMaxHoles}, press 'space'", kAppWidth/2, 2*kAppHeight/3, size=75, fill=kTutorialTextColor, border='black', borderWidth=2)

def drawScore(app):
    drawRect(0,0,165,120,fill=kTutorialColor)
    drawBorder(0,0,165, 120, 3)
    drawLabel(f'Score: {app.courseScore}', kScoreTextBuffer, kScoreTextBuffer, align='left-top', size=kScoreTextSize)
    drawLabel(f'Hole: {app.currHole} Par: {app.course.calculatePar()}', kScoreTextBuffer, 2*kScoreTextBuffer+kScoreTextSize, align='left-top', size=kScoreTextSize)
    drawLabel(f'Hole Throws: {app.holeScore}', kScoreTextBuffer, 3*kScoreTextBuffer+2*kScoreTextSize, align='left-top', size=kScoreTextSize)

def drawBorder(posX, posY, width, height, borderWidth, align='left-top'):
    drawRect(posX,posY,width, height, fill=None, border='darkGray', borderWidth=borderWidth, align=align)
    if align=='top': 
        drawRect(posX,posY+borderWidth,width-2*borderWidth, height-2*borderWidth, fill=None, border='silver', borderWidth=borderWidth, align=align)
    else:
        drawRect(posX+borderWidth,posY+borderWidth,width-2*borderWidth, height-2*borderWidth, fill=None, border='silver', borderWidth=borderWidth, align=align)

def drawSplash(app):
    game3D.drawBackground(app)
    game3D.drawTree(app, Tree(700, kAppHeight/4, 300), 1)
    game3D.drawTree(app, Tree(700, kAppHeight/6, 300), 1.15)
    game3D.drawTree(app, Tree(700, 100, 300), 1.3)
    game3D.drawGeyser(app, app.splashGeyser, 1)
    game3D.drawTree(app, Tree(700, 5*kAppHeight/7, 300), 1.5)
    game3D.drawTree(app, Tree(600, 3*kAppHeight/4, 300), 1)
    drawBorder(0, 0, kAppWidth, kAppHeight, 10)
    labelRot = math.sin(time.time()*kOpeningScreenTimeFactor) * 20
    drawImage(kGoalPath, 2*kAppWidth/3, 3*kAppHeight/4, align='center', width=200, height=400)
    fill = gradient('lightCyan', *[kFrisbeeColor]*int(60//30), 'skyBlue', 'steelBlue', start='top')
    drawLabel('SUPER PAPER FRISBEE GOLF', kAppWidth/2, kAppHeight/4, rotateAngle = labelRot, size=60, fill='red', border='dimGray', borderWidth=3, bold=True)
    drawOval(kAppWidth/3, 3*kAppHeight/5, 100, 300, fill=fill, rotateAngle=-40,border=kDiscGradient, borderWidth=kDiscBorderWidth)
    drawLabel('press any key to start', kAppWidth/2, kAppHeight-100, rotateAngle = -labelRot, size=20, fill='red', border='dimGray', borderWidth=1)

# tutorial draw steps
def drawTutorialStep(app):
    match app.tutorialStep:
        case 0:
            game2D.drawGame(app)
            drawRect(kAppWidth/2, kAppHeight/4, kAppWidth/2, kAppHeight/8,  fill=kTutorialColor, opacity=kTutorialOpacity, align='top')
            drawBorder(kAppWidth/2, kAppHeight/4, kAppWidth/2, kAppHeight/8, kTutorialBorderWidth, align='top')
            drawLabel('Welcome to Super Paper Frisbee Golf! Your goal is to throw the frisbee across the field', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+kScoreTextBuffer, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('into the red goal on the right in fewer throws than the par. Be careful of the obstacles!', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+2*kScoreTextBuffer+kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('Press any key to continue.', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+3*kScoreTextBuffer+2*kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
        case 1:
            game2D.drawGame(app)
            drawRect(kAppWidth/2, kAppHeight/4, kAppWidth/2, kAppHeight/4,  fill=kTutorialColor, opacity=kTutorialOpacity, align='top')
            drawBorder(kAppWidth/2, kAppHeight/4, kAppWidth/2, kAppHeight/4, kTutorialBorderWidth, align='top')
            drawLabel('The following are the obstacles to avoid, each with different properties.', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+kScoreTextBuffer, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('walls and trees will stop your frisbee, while orange bouncy walls will reflect the frisbee.', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+2*kScoreTextBuffer+kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('Geysers will not impede your frisbee, but will shoot it upwards if the geyser is active.', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+3*kScoreTextBuffer+2*kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawRect(4*kAppWidth/12, 2*kAppHeight/5+20, kObstacleThickness, 100, align='center', border=kBouncyColor, borderWidth = 5)
            drawImage(kTreeTopPath, 5*kAppWidth/12, 2*kAppHeight/5+20, align='center', borderWidth=2)
            drawRect(7*kAppWidth/12, 2*kAppHeight/5+20, kObstacleThickness, 100, align='center', fill=kWallColor)
            drawImage(kGeyserTopDownPath, 8*kAppWidth/12, 2*kAppHeight/5+20, align='center')
            
        case 2:
            game2D.drawGame(app)
            drawSliders(*app.sliders2D)
            drawRect(kAppWidth/2, kAppHeight/4, kAppWidth/2, kAppHeight/8,  fill=kTutorialColor, opacity=kTutorialOpacity, align='top')
            drawBorder(kAppWidth/2, kAppHeight/4, kAppWidth/2, kAppHeight/8, kTutorialBorderWidth, align='top')
            drawLabel('Click to change the direction of your throw.', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+kScoreTextBuffer, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('In the bottom right you have sliders to control the power and roll of your throw. Adjusting', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+2*kScoreTextBuffer+kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('the roll will cause the frisbee to curve left or right. To adjust, click and drag the bar.', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+3*kScoreTextBuffer+2*kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)

        case 3:
            game3D.drawGame(app)
            drawRect(kAppWidth/2, kAppHeight/4, kAppWidth/2, kAppHeight/8,  fill=kTutorialColor, opacity=kTutorialOpacity, align='top')
            drawBorder(kAppWidth/2, kAppHeight/4, kAppWidth/2, kAppHeight/8, kTutorialBorderWidth, align='top')
            drawLabel('Welcome to the 3D view! Here you can see how high obstacles are (some walls are', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+kScoreTextBuffer, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('short enough to throw over). ', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+2*kScoreTextBuffer+kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('To switch between views press \'tab\'. Every course is completely randomly generated.', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+3*kScoreTextBuffer+2*kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            
        case 4:
            game3D.drawGame(app)
            drawSliders(*app.sliders3D)
            drawRect(kAppWidth/2, kAppHeight/4, kAppWidth/2, 3*kAppHeight/16,  fill=kTutorialColor, opacity=kTutorialOpacity, align='top')
            drawBorder(kAppWidth/2, kAppHeight/4, kAppWidth/2, 3*kAppHeight/16, kTutorialBorderWidth, align='top')
            drawLabel('In the bottom right you have sliders to control the upwards power of your throw and', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+kScoreTextBuffer, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('pitch of the frisbee. Positive pitch will let the frisbee float better as it flies,', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+2*kScoreTextBuffer+kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('negative will quickly bring it down. Press \'space\' to throw. ', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+3*kScoreTextBuffer+2*kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('Watch out for the wind! (wind will influence the disc more if it is tilted)', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+4*kScoreTextBuffer+3*kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)

        case 5:
            game2D.drawGame(app)
            drawSliders(*app.sliders2D)
            drawScore(app)
            drawWind(app)
            drawRect(kAppWidth/2, kAppHeight/4, kAppWidth/2, 3*kAppHeight/16,  fill=kTutorialColor, opacity=kTutorialOpacity, align='top')
            drawBorder(kAppWidth/2, kAppHeight/4, kAppWidth/2, 3*kAppHeight/16, kTutorialBorderWidth, align='top')
            drawLabel('In the bottom left you will find the wind indicator, this will show you the direction', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+kScoreTextBuffer, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('and power of the wind. Red is the strongest wind, green is the weakest. Some courses', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+2*kScoreTextBuffer+kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('are too long to fit on your screen, use the arrow keys in either view to pan left', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+3*kScoreTextBuffer+2*kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)
            drawLabel('and right. Your score is in the top left and will update after each hole.', kAppWidth/4+kScoreTextBuffer, kAppHeight/4+4*kScoreTextBuffer+3*kScoreTextSize, size=kScoreTextSize, align='left-top', fill=kTutorialTextColor)


def drawWind(app):
    drawWindLines(app)
    x, y = kWindPos
    drawLine(x, y, x+app.wind.x*20, y + app.wind.y*20, arrowEnd = True, fill=game2D.getColorForPercentage(min(1, app.wind.magnitude() / 5)))
    drawLabel('Wind', x, y, size=20, border='white', borderWidth=2)
    if app.drawLabels:
        drawLabel(int(10*app.course.wind.magnitude())/10, x, y+25, size=20)

def drawWindLines(app):
    for line in app.windLines:
        x, y = line.x, line.y
        drawLine(x, y, x+app.wind.x*20, y + app.wind.y*20, fill='white', opacity=kWindLineOpacity)

def drawControls(app):
    if app.showControls:
        drawLabel("'tab' to switch view, click to aim, 'space' to throw. Click and drag to adjust sliders, 'r' to reset throw", app.width/2, 30, size=20)
    else:
        drawLabel("'c' to show controls", app.width/2, 30, size=20)


def redrawAll(app):
    if app.isStarting:
        drawSplash(app)
    elif app.isTutorial:
        drawTutorialStep(app)
    elif app.isCourseOver:
        drawGameOver(app)
    else:
        startTime = time.time()
        if app.isTopDown:
            game2D.drawGame(app)
            drawSliders(*app.sliders2D)
            drawWind(app)
        else:
            game3D.drawGame(app)
            drawSliders(*app.sliders3D)
        drawFPS(app, startTime)
        drawScore(app)
        if app.showControls:
            drawControls(app)
        if app.scored:
            drawLabel('GOAL!', kAppWidth/2, kAppHeight/2, size=100, border='white', borderWidth=4)
            holeScore = app.holeScore-app.course.calculatePar()
            drawLabel(f'Hole Score: {holeScore if holeScore != 0 else "Par!"}', kAppWidth/2, kAppHeight/2 + 100, size=100, border='white', borderWidth=4)

def main():
    runApp()

main()