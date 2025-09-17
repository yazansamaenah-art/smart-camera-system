from smartpole.edge.hal.sensors import SensorHub

def test_sensor_capture():
    hub=SensorHub(); fr=hub.capture(); assert fr.data.shape[2]==3
