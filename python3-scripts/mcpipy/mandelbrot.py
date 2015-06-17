#
# MIT-licensed code by Alexander Pruss
#

from .mc import *
from . import mcpi.settings
import cmath
import time
import sys

ESCAPE = 256
if len(sys.argv) < 2:
    SIZE = 640 if not mcpi.settings.isPE else 400
else:
    SIZE = int(sys.argv[1])

if len(sys.argv) < 3:
    formula = lambda z,c : z * z + c
else:
    formula = eval('lambda z,c : '+sys.argv[2])

black = WOOL_BLACK
#palette = ( WOOL_WHITE, WOOL_ORANGE, WOOL_MAGENTA, WOOL_LIGHT_BLUE,
#            WOOL_YELLOW, WOOL_LIME, WOOL_PINK, WOOL_GRAY, WOOL_LIGHT_GRAY,
#            WOOL_CYAN, WOOL_PURPLE, WOOL_BLUE, WOOL_BROWN, WOOL_GREEN,
#            WOOL_RED, 152 )


# palette generated by solving traveling salesman problems in RGB space
#palette = (WOOL_WHITE,WOOL_LIGHT_GRAY,WOOL_LIGHT_BLUE,WOOL_CYAN,WOOL_LIME,WOOL_YELLOW,WOOL_ORANGE,152,WOOL_RED,WOOL_BROWN,WOOL_GREEN,WOOL_GRAY,WOOL_BLUE,WOOL_PURPLE,WOOL_MAGENTA,WOOL_PINK)
palette = (WOOL_WHITE,HARDENED_CLAY_STAINED_WHITE,WOOL_PINK,WOOL_MAGENTA,WOOL_PURPLE,HARDENED_CLAY_STAINED_LIGHT_BLUE,HARDENED_CLAY_STAINED_CYAN,HARDENED_CLAY_STAINED_PURPLE,HARDENED_CLAY_STAINED_LIGHT_GRAY,HARDENED_CLAY_STAINED_MAGENTA,HARDENED_CLAY_STAINED_PINK,HARDENED_CLAY_STAINED_RED,WOOL_RED,REDSTONE_BLOCK,HARDENED_CLAY_STAINED_ORANGE,WOOL_ORANGE,HARDENED_CLAY_STAINED_YELLOW,WOOL_YELLOW,WOOL_LIME,HARDENED_CLAY_STAINED_LIME,HARDENED_CLAY_STAINED_GREEN,WOOL_GREEN,HARDENED_CLAY_STAINED_GRAY,WOOL_BROWN,HARDENED_CLAY_STAINED_BROWN,WOOL_GRAY,HARDENED_CLAY_STAINED_BLUE,WOOL_BLUE,WOOL_CYAN,WOOL_LIGHT_BLUE,WOOL_LIGHT_GRAY)

def escapeTime(c):
    i = 0
    z = c
    try:
        while abs(z) < 2 and i < ESCAPE:
            i = i + 1
            z = formula(z,c)
        return i
    except:
        return -1

#
# we could of course just do for x in range(0,size): for y in range(0,size): yield(x,y)
# but it will make users happier if we start at the player
#

def loopGenerator(size, cenX, cenY):
    yield (cenX, cenY)
    for r in range(1,size):
        # right line segment
        if cenX+r < size:
            y = cenY - r
            if y < 0:
                y = 0
            while y < cenY + r and y < size:
                yield (cenX+r, y)
                y += 1
        # top line segment
        if cenY+r < size:
            x = cenX + r
            if x >= size:
                x = size - 1
            while cenX - r < x and 0 <= x:
                yield (x, cenY+r)
                x -= 1
        # left line segment
        if 0 <= cenX-r:
            y = cenY + r
            if y >= size:
                y = size - 1
            while cenY - r < y and 0 <= y:
                yield (cenX-r, y)
                y -= 1
        # bottom line segment
        if 0 <= cenY-r:
            x = cenX - r
            if x < 0:
                x = 0
            while x < cenX + r and x < size:
                yield(x, cenY - r)
                x += 1

def pollZoom():
    global lastHitEvent
    events = mc.events.pollBlockHits()
    if len(events) == 0:
        return lastHitEvent != None
    lastHitEvent = events[-1]
    return True

def toComplex(x,y):
    return  complex((x - centerMC.x) * scale  + centerCx.real,
                    (y - centerMC.z) * scale  + centerCx.imag)

def draw():
    count = 0
    for (x,y) in loopGenerator(SIZE, SIZE/2, SIZE/2):
        mcX = x + centerMC.x - SIZE/2
        mcY = y + centerMC.z - SIZE/2
        c = toComplex(mcX, mcY)

        esc = escapeTime(c)
        if esc < 0:
            block = AIR
        elif esc < ESCAPE:
            block = palette[esc % len(palette)]
        else:
            block = black
        mc.setBlock(mcX, centerMC.y, mcY,block)
        if count >= 1000:
            if pollZoom():
                break
            else:
                count = 0
        else:
            count += 1

def formatComplex(z):
    return "%.2g+%.2gi" % (z.real,z.imag)

def getInfo():
    return ( "Center: "+formatComplex(centerCx)+", range from "+
             formatComplex(toComplex(centerMC.x - SIZE/2, centerMC.z - SIZE/2))+" to "+
             formatComplex(toComplex(centerMC.x + SIZE/2 - 1, centerMC.z + SIZE/2 - 1)) )

mc = Minecraft()
centerMC = mc.player.getPos()
centerMC.ifloor()
adjustedPlayer = centerMC.clone()
adjustedPlayer.y += 1
centerCx = complex(0,0)
scale    = 4. / SIZE
lastHitEvent = None

while True:
    mc.player.setPos(adjustedPlayer)
    mc.postToChat(getInfo())
    draw()
    mc.postToChat("Rendered")
    while not pollZoom():
        time.sleep(0.25)
    if ( lastHitEvent.pos.y != centerMC.y or
         lastHitEvent.pos.x < centerMC.x - SIZE / 2 or
         lastHitEvent.pos.x >= centerMC.x + SIZE / 2 or
         lastHitEvent.pos.z < centerMC.z - SIZE / 2 or
         lastHitEvent.pos.z >= centerMC.z + SIZE / 2 ):
            mc.postToChat("resetting")
            centerCx = complex(0,0)
            scale = 4. / SIZE
    else:
            mc.postToChat("zooming")
            centerCx = toComplex(lastHitEvent.pos.x,lastHitEvent.pos.z)
            scale /= 2
    lastHitEvent = None
