import json
import requests
from datatypes import Location, Client
import env
import bs4
import math

def get_location(ip):
    # Returns: (Latitude: str, Longitude: str)
    # Raises: RuntimeError
    api_key = env.key
    # api url
    url = f"https://api.apilayer.com/ip_to_location/{ip}"

    headers= {
        "apikey": f"{api_key}"
    }

    response = requests.get(url, headers=headers)

    result = response.text
    result = json.loads(result)
    if response.status_code >= 400:
        raise RuntimeError("Malformed request")
    return Location(float(result["latitude"]), float(result["longitude"]))


def distance(loc_1: Location, loc_2: Location) -> float:


    # calculate the distance between 2 points and returns a distance in km.
    radius = 6371  # km

    dlat = math.radians(loc_2.latitude - loc_1.latitude)
    dlon = math.radians(loc_2.longitude - loc_1.longitude)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(loc_1.latitude)) * math.cos(math.radians(loc_2.latitude)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d # distance in km

def intersect(client_1: Client, client_2: Client) -> bool:
    
    return False


if __name__ == "__main__":
    loc_1 = Location(10.1824542, -25.1389054)
    
    loc_2 = Location(45.0123102, -231.120943)

    print(distance(loc_1, loc_2))

    