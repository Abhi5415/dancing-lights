import time
from rpi_ws281x import PixelStrip, Color
from cfg import strip


class Panel:
    brightness = 0  # range from 0 to 255
    color = (0, 0, 0)  # RGB tuple
    colorShiftRate = 0.01  # percentage per millisecond
    brightnessShiftRate = 0.001
    deadzone = 5

    def __init__(self, panelLocation: list) -> None:
        self.panelLocation = panelLocation

    def setPanel(self, targetColor, brightness=0):
        self.targetColor = targetColor
        self.brightness = brightness
        self.update()

    def update(self):
        newColor = list(self.color)
        increment = [
            abs(self.color[i] - self.targetColor[i]) * self.colorShiftRate
            for i in range(3)
        ]
        for x in range(int(1 / self.colorShiftRate)):
            for i in range(3):
                if (
                    not self.targetColor[i] - self.deadzone
                    < newColor[i]
                    < self.targetColor[i] + self.deadzone
                ):
                    if newColor[i] < self.targetColor[i]:
                        newColor[i] += increment[i]
                    else:
                        newColor[i] -= increment[i]
            for i in range(self.panelLocation[0], self.panelLocation[1]):
                r, g, b = map(int, newColor)
                strip.setPixelColor(i, Color(r, g, b))
            strip.show()
            # print(r, g, b)
            time.sleep(0.01)
        for i in range(self.panelLocation[0], self.panelLocation[1]):
            r, g, b = map(int, self.targetColor)

            strip.setPixelColor(i, Color(r, g, b))
        strip.show()
        self.color = tuple(self.targetColor)
