import json
import requests
from types import Location, Client
import env
import bs4
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
    # calculate the distance between 2 points
    return 0

def intersect(client_1: Client, client_2: Client) -> bool:
    
    return False