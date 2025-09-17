import numpy as np
from smartpole.edge.ai.pipeline import AIPipeline

def test_pipeline_detects_vehicle():
    pipe=AIPipeline('opencv')
    img=np.zeros((240,320,3),dtype=np.uint8); img[100:130,10:70,:]=255
    out=pipe.process(img); assert out['objects']
