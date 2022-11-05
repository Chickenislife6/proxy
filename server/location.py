import requests
import env
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
    if response.status_code >= 400:
        raise RuntimeError("Malformed request")
    return (result["latitude"], result["longitude"])
