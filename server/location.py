import json
import time
import requests
from datatypes import Location, Client
import env
import math

def get_location(ip):

    # Returns: (Latitude: str, Longitude: str)
    # Raises: RuntimeError
    if (ip == "127.0.0.1"):
        return Location(0, 0)
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

def intersect(client_1: Client, client_2: Client) -> bool: # returns True if clients are intersecting one another, False otherwise

    dist = distance(client_1.location, client_2.location) # distance between the two clients

    # calculate elapsed time for both clients
    current_time = time.time()
    c1_elapsed = current_time - client_1.time # gives time in seconds
    c2_elapsed = current_time - client_2.time

    # calculate distance "covered" by both clients
    c1_dist = c1_elapsed * client_1.speed # speed is in km per second
    c2_dist = c2_elapsed * client_2.speed

    if dist < c1_dist + c2_dist:
        return True

    else:
        return False


if __name__ == "__main__":
    loc_1 = Location(1, 0) # NYC coordinates
    
    loc_2 = Location(-1, 0) # LA coordinates

    print(distance(loc_1, loc_2))
