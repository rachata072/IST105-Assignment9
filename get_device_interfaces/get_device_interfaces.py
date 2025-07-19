import requests
from requests.auth import HTTPBasicAuth
from dnac_config import DNAC_IP, DNAC_PORT, DNAC_USER, DNAC_PASSWORD


def get_auth_token():
    """
    Retrieves the authentication token from Cisco DNA Center
    """
    url = f"https://{DNAC_IP}:{DNAC_PORT}/dna/system/api/v1/auth/token"
    response = requests.post(
        url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASSWORD), verify=False
    )

    if response.status_code == 200:
        return response.json()["Token"]
    else:
        print("Failed to retrieve token:", response.text)
        return None


def get_device_list(token):
    """
    Retrieves the list of network devices
    """
    url = f"https://{DNAC_IP}:{DNAC_PORT}/dna/intent/api/v1/network-device"
    headers = {"x-auth-token": token, "Content-Type": "application/json"}

    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve devices:", response.text)
        return None


def get_device_id(device_json, token):
    """
    Iterates over the retrieved devices and fetches their interfaces
    """
    for device in device_json.get("response", []):
        print(f"Fetching Interfaces for Device ID ----> {device['id']}\n")
        get_device_int(device["id"], token)
        print("\n")


def get_device_int(device_id, token):
    """
    Retrieves device interface information
    """
    url = f"https://{DNAC_IP}:{DNAC_PORT}/dna/intent/api/v1/interface"
    headers = {"x-auth-token": token, "Content-Type": "application/json"}
    querystring = {"macAddress": device_id}

    response = requests.get(url, headers=headers, params=querystring, verify=False)

    if response.status_code == 200:
        print_interface_info(response.json())
    else:
        print("Failed to retrieve interface info:", response.text)


def print_interface_info(interface_info):
    """
    Prints the interface information in a formatted table
    """
    print(
        "{0:42}{1:17}{2:12}{3:18}{4:17}{5:10}{6:15}".format(
            "portName",
            "vlanId",
            "portMode",
            "portType",
            "duplex",
            "status",
            "lastUpdated",
        )
    )

    for intf in interface_info.get("response", []):
        print(
            "{0:42}{1:10}{2:12}{3:18}{4:17}{5:10}{6:15}".format(
                str(intf.get("portName", "N/A")),
                str(intf.get("vlanId", "N/A")),
                str(intf.get("portMode", "N/A")),
                str(intf.get("portType", "N/A")),
                str(intf.get("duplex", "N/A")),
                str(intf.get("status", "N/A")),
                str(intf.get("lastUpdated", "N/A")),
            )
        )


if __name__ == "__main__":
    token = get_auth_token()
    if token:
        devices = get_device_list(token)
        if devices:
            get_device_id(devices, token)
