# from cfg import strip
import time
from panel import Panel

p = Panel((0, 89))
p.colorShiftRate = 0.001


def update():
    p.update()


p.setPanel((0, 0, 0))
while True:
    update()
    p.setPanel((255, 255, 255))
    time.sleep(0.1)
