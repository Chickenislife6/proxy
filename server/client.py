from dataclasses import dataclass

from SomeServerProtocol import SomeServerProtocol

@dataclass
class Location():
    latitude: float
    longitude: float

@dataclass
class Client():
    object: SomeServerProtocol
    partner: str
    location: Location
    time: int