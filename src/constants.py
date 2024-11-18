from cmu_graphics import gradient, rgb
kAppWidth, kAppHeight = 1600, 1000
kAppInitPauseState = False

kSpeedResistance = 0.1     # resistance to speed based on current speed - PERCENTAGE
kPitchResistance = 0.1     # resistance to speed based on current pitch - PERCENTAGE
kRollFactor      = 0.05    # roll increase based on current roll - PERCENTAGE 
kRollFactorReduction = 1/5 # roll increase reduction based on current roll - RATIO
kleftSpeedFactor = 5.0     # side speed increase factor based on current roll - PERCENTAGE
kGravity = -.4              # downward acceleration due to gravity - UNITS / STEP / STEP

kMaxPlayerAcceleration = 10
kMaxPlayerSpeed = 50
kPositionAccuracy = 20

kRollControlMultiplier = 1 / 10
kAimControlMultiplier = 1 / 4

kStepsPerSecond = 30 
kMotionStepsPerSecond = 5
kMotionTimeFactor = kMotionStepsPerSecond / kStepsPerSecond

kTrailLength = 5
kTrailOpacity = 40
kTrailWidth = 3
kDiscBorderWidth = 4
kFrisbeeSize = 30
kFrisbeeColor = 'lightBlue'
kTrailColor = kFrisbeeColor
kShadowColor = 'black'
kDiscGradient = gradient(*[kFrisbeeColor]*4, 'skyBlue', 'steelBlue', start='center')

kGrassLight, kGrassMedium, kGrassDark = rgb(20, 150, 50), rgb(30, 125, 30), rgb(20, 100, 10)

kBackgroundGradient0 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//80), start='left')
kBackgroundGradient1 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//80), start='center')
kBackgroundGradient2 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassDark, kGrassMedium]*(kAppWidth//200), start='top')
kBackgroundGradient3 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassMedium]*(kAppWidth//150), start='left-top')
kBackgroundGradient4 = gradient(*[kGrassLight, kGrassMedium, kGrassDark, kGrassDark, kGrassMedium]*(kAppWidth//300), start='right-top')

kTeamColors = ['black', 'white']