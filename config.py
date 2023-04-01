# In-game settings ------------

displayPlayerGrid = False
displayCPUGrid = True

FPS_CAP = 60  # Pygame clock tick frame rate

DAS = 8  # Delayed Auto Shift, in ticks (min: 1) - how long the left or right key has to be held before the piece repeatedly starts moving left or right;
ARR = 2  # Auto-Repeat Rate, in ticks + 1 (ARR=1 results in 2 ARR for some reason...) - after DAS is engaged, how many ticks to wait between left or right movements.
SDS = 1  # Soft Drop Speed, gravity delay in ticks under soft drop (min: 0)
ARE = 6  # Piece entry delay, in ticks (min: 0)
LCD = 15  # Line clear delay, in ticks (min: 1)

fast = False  # Overrides above settings for faster settings. (listed all the way down below)
veryFast = False  # Used to debug AI

# BOT CONTROL

cpuWaitMin = 1
cpuWaitMax = 4
tetrisWeight = 1  # 0-1.5. defines how greedy the bot is. 0 is extremely defensive, 0.75 is quite balanced while 1.25 is pretty aggressive.
cpuHardDrop = True  # if False, forces the CPU to soft drop its piece.
instantCPUPlacement = False

# Enable terrible implementations of IHS and IRS mainly because they
# trigger upon a single keypress instead of checking if the button has been held
# like in guideline games
IHSEnabled = True
IRSEnabled = True

nextQueue = 6  # number of next Tetrominoes displayed (0-6)

maxLockResets = 16  # Max number of times lock delay can reset after a successful rotation
lockDelay = 30  # ticks
startingSpeedLv = 0 # 1-20, 21-60 (M1-M40)
speedLvCap = 10
speedLvLines = 999  # how many lines to clear to advance speed lv?

bagContents = 0  # 0: setups game with standard Tetrominoes, 1: play with Triminoes, 2: play with Giant pieces
bagType = 0 # How pieces are dealt. 0: '7-bag', 1: Random, 2: Debug

alwaysRefreshDisplay = False
hideField = False
hideTime = 6

debugFrameRate = False

# Internal variables ----------

gameGridX, gameGridY = 10, 20  # range (4-30)

cellSizePx = 30
bkgColor = (212, 218, 223)
gridBorderColor = (252, 255, 240)
gridBkgColor = (87, 87, 104)
cellBorderColor = (96, 96, 115)
minoBorderColor = (234, 234, 238)

screenXExtra, screenYExtra = 925, 175  # original: 925, 175
numGrids = 2  # This setting does not add more grids by itself.
if not displayCPUGrid or not displayPlayerGrid:
        numGrids = 1
        screenXExtra = 775  # original: 575
screenX = cellSizePx * gameGridX * numGrids + screenXExtra
screenY = cellSizePx * gameGridY + screenYExtra

renderedCellsAbove = 5



# Respectively: null, I, J, L, O, S, T, Z, grey
tetColors = [
        (),
        (107, 222, 228),
        (133, 133, 233),
        (234, 172, 132),
        (247, 240, 111),
        (155, 231, 109),
        (209, 143, 231),
        (247, 134, 128),
        (147, 147, 174),
        (217, 217, 240)
        ]
# Speed data: [idx = speed lv.] (wait frames, number of cells moved down)
speedData = [
        (60, 0),  # Lv. 0 - Unused
        (120, 1),  # Lv. 1
        (60, 1),
        (50, 1),
        (40, 1),
        (30, 1),  # Lv. 5
        (24, 1),
        (18, 1),
        (12, 1),
        (9, 1),
        (8, 1),  # Lv. 10
        (7, 1),
        (6, 1),
        (5, 1),
        (4, 1),
        (3, 1),  # Lv. 15
        (2, 1),
        (1, 1),
        (1, 2),
        (1, 3),
        (1, 20),  # Lv. 20
]

# Master speed data: [idx = master speed lv.] (lock frames, line clear delay in frames, new DAS)
masterSpeedData = [
        (45, 20, 8),  # M0, unused
        (42, 18, 8),  # M1
        (40, 16, 8),
        (37, 14, 7),
        (35, 12, 7),
        (33, 10, 7),  # M5
        (31, 8, 7),
        (30, 6, 7),
        (29, 4, 7),
        (29, 2, 7),
        (29, 1, 6),  # M10
        (28, 1, 6),
        (27, 1, 6),
        (26, 1, 6),
        (25, 1, 6),
        (24, 1, 6),  # M15
        (23, 1, 5),
        (22, 1, 5),
        (21, 1, 5),
        (20, 1, 5),
        (19, 1, 5),
        (18, 1, 4),  # M20
        (17, 1, 4),
        (16, 1, 4),
        (15, 1, 4),
        (14, 1, 4),
        (13, 1, 4),  # M25
        (12, 1, 4),
        (11, 1, 4),
        (10, 1, 4),
        (9, 1, 4),
        (8, 1, 4),  # M30
        (7, 1, 4),  # M31
        (6, 1, 4),  # M32
        (5, 1, 4),  # M33
        (5, 1, 4),  # M34
        (4, 1, 4),  # M35
        (4, 1, 4),  # M36
        (3, 1, 4),  # M37
        (3, 1, 4),  # M38
        (2, 1, 3),  # M39
        (2, 1, 2)  # M40
]

if fast:
        DAS = 5
        ARR = 2
        ARE = 0
        LCD = 5
        SDS = 0

if veryFast:
        LCD = 1
        FPS_CAP = 9999
        speedLvLines = 9999
        
if displayCPUGrid and displayPlayerGrid:
        FPS_CAP *= 5
        DAS *= 2
        ARR += 1
        SDS += 1

if displayCPUGrid and not displayPlayerGrid:
    ARR = 3
