from pydantic import BaseModel
class Location(BaseModel):
    lat: float; lon: float
class EventIn(BaseModel):
    timestamp: float
    type: str
    location: Location
    payload: dict
    source: str = 'edge'
