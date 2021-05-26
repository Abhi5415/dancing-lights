from cfg import strip
import time
from panel import Panel

panels = [
    Panel([0, 8]),
    Panel([8, 17]),
    Panel([17, 26]),
    Panel([26, 35]),
    Panel([35, 44]),
    Panel([44, 53]),
    Panel([53, 62]),
    Panel([62, 71]),
    Panel([71, 80]),
    Panel([80, 89]),
]


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return list(map(lambda x: x & 255, (pos * 3, 255 - pos * 3, 0)))
    elif pos < 170:
        pos -= 85
        return list(map(lambda x: x & 255, (255 - pos * 3, 0, pos * 3)))
    else:
        pos -= 170
        return list(map(lambda x: x & 255, (0, pos * 3, 255 - pos * 3)))


def rainbowLight(j):
    for i in range(len(panels)):
        panels[i].setColor(wheel(j), 0.01)


def bassLight(drop: bool):
    if drop:
        for i in panels:
            i.setColor([180, 180, 180], 0.9)
    else:
        for i in panels:
            i.setColor([20, 20, 20], 0.01)


# for i in panels:
#     i.setColor(rate=1)
#     i.update()

# while True:
#     idx += 1

#     if mode == "rainbow":
#         rainbow(idx)

#     if idx > 256:
#         idx = 0

#     for i in panels:
#         i.update()

#     time.sleep(0.02)
