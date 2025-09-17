import time, random
from dataclasses import dataclass
from typing import Tuple
import numpy as np

@dataclass
class Frame:
    data: np.ndarray
    timestamp: float
    gps: Tuple[float, float]

class CameraSensor:
    def __init__(self, width=320, height=240):
        self.width=width; self.height=height; self.t=0
    def read(self):
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        x = (10 + (self.t * 5)) % (self.width - 60); y = 100
        img[y:y+30, int(x):int(x)+60, :] = 255
        self.t += 1; return img

class GPSSensor:
    def __init__(self, lat=37.7749, lon=-122.4194):
        self.lat=lat; self.lon=lon
    def read(self):
        return (self.lat + random.uniform(-0.0005, 0.0005),
                self.lon + random.uniform(-0.0005, 0.0005))

class AirQualitySensor:
    def read(self): return 400 + random.uniform(-20,60)

class SensorHub:
    def __init__(self):
        self.camera=CameraSensor(); self.gps=GPSSensor(); self.aqi=AirQualitySensor()
    def capture(self):
        return Frame(self.camera.read(), time.time(), self.gps.read())
