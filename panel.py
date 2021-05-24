import time
from rpi_ws281x import PixelStrip, Color
from cfg import strip


class Panel:
    brightness = 1.0  # range from 0 to 1.0
    targetBrightness = 1.0
    currentColor = [0, 0, 0]  # RGB tuple
    colorShiftRate = 0.1  # percentage per millisecond
    deadzone = 5
    panelLocation = []
    targetColor = [0, 0, 0]
    delta = [0, 0, 0]

    def __init__(self, panelLocation: list) -> None:
        self.panelLocation = panelLocation

    def setBrightness(self, targetBrightness=1.0, rate=1):
        self.colorShiftRate = rate
        self.brightness = targetBrightness
        self.__setdelta()

    def setColor(self, targetColor=[255, 255, 255], rate=0.001):
        self.colorShiftRate = rate
        self.targetColor = targetColor
        self.__setdelta()

    def update(self):
        changed = False
        for i in range(3):
            # print(abs(self.targetColor[i] - self.currentColor[i]), abs(self.delta[i]))
            if abs(float(self.targetColor[i] - self.currentColor[i])) < abs(
                self.delta[i]
            ):
                if self.currentColor[i] != self.targetColor[i]:
                    self.currentColor[i] = self.targetColor[i]
                    changed = True
            else:
                self.currentColor[i] += self.delta[i]
                changed = True

        if changed:
            self.__set()

    def __set(self):
        r, g, b = map(int, self.currentColor)
        # print(self.panelLocation, r, g, b)

        for i in range(self.panelLocation[0], self.panelLocation[1]):
            strip.setPixelColor(i, Color(r, g, b))
    

    def __setdelta(self):
        self.delta = [
            ((self.targetColor[i] * self.brightness) - self.currentColor[i])
            * self.colorShiftRate
            for i in range(3)
        ]
