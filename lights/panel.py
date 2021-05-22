import time
from rpi_ws281x import PixelStrip, Color
from cfg import strip


class Panel:
    brightness = 0  # range from 0 to 255
    color = (0, 0, 0)  # RGB tuple
    colorShiftRate = 0.1  # percentage per millisecond
    brightnessShiftRate = 0.1
    deadzone = 5

    def __init__(self, panelLocation: list) -> None:
        self.panelLocation = panelLocation

    def setPanel(self, targetColor, brightness=0):
        self.targetColor = targetColor
        self.brightness = brightness
        self.update()

    def update(self):
        newColor = [0, 0, 0]
        while True:
            for i in range(3):
                if self.color[i] < self.targetColor[i]:
                    newColor[i] += (
                        abs(self.color[i] - self.targetColor[i]) * self.colorShiftRate
                    )
                else:
                    newColor[i] -= (
                        abs(self.color[i] - self.targetColor[i]) * self.colorShiftRate
                    )
            for i in range(self.panelLocation[0], self.panelLocation[1]):
                r, g, b = newColor
                strip.setPixelColor(i, Color(r, g, b))
                time.sleep(0.001)

        self.color = newColor
