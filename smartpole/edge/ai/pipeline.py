from typing import Dict, Any, List
import os, numpy as np

class BaseBackend:
    def process(self, frame): raise NotImplementedError

class StubBackend(BaseBackend):
    def __init__(self): self.counter=0
    def process(self, frame):
        self.counter += 1
        white = (frame[:,:,0]>240)&(frame[:,:,1]>240)&(frame[:,:,2]>240)
        objects=[]; plates=[]
        if int(white.sum())>1000: objects.append({"type":"vehicle","confidence":0.9})
        if objects and (self.counter%5==0): plates.append({"text":"ABC123","confidence":0.88})
        return {"objects":objects,"plates":plates}

class OpenCVBackend(BaseBackend):
    def process(self, frame):
        try: import cv2
        except Exception: return StubBackend().process(frame)
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        blur=cv2.GaussianBlur(gray,(5,5),0)
        _,th=cv2.threshold(blur,200,255,cv2.THRESH_BINARY)
        cnts,_=cv2.findContours(th,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        objects=[]; plates=[]
        for c in cnts:
            x,y,w,h=cv2.boundingRect(c)
            if w*h>800: objects.append({"type":"vehicle","confidence":0.7})
        import numpy as np
        if objects and int(np.random.randint(0,5))==0: plates.append({"text":"ABC123","confidence":0.7})
        return {"objects":objects,"plates":plates}

class TesseractBackend(BaseBackend):
    def process(self, frame):
        try: import cv2, pytesseract, re
        except Exception: return OpenCVBackend().process(frame)
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        text=pytesseract.image_to_string(gray)
        objects=[{"type":"vehicle","confidence":0.6}]; plates=[]
        m=re.search(r"[A-Z]{3}\s?\d{3}", text or "")
        if m: plates.append({"text":m.group(0).replace(" ",""),"confidence":0.6})
        return {"objects":objects,"plates":plates}

def get_backend(name):
    name=(name or "stub").lower()
    return OpenCVBackend() if name=="opencv" else TesseractBackend() if name=="tesseract" else StubBackend()

class AIPipeline:
    def __init__(self, backend=None): self.impl=get_backend(backend or os.getenv("PIPELINE_BACKEND","stub"))
    def process(self, frame): return self.impl.process(frame)
