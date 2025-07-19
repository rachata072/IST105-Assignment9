import os
from django.shortcuts import render
from django.http import HttpResponse
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import datetime
from pymongo import MongoClient
import sys

# Import DNAC config variables
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../get_device_interfaces')))
from dnac_config import DNAC_IP, DNAC_PORT, DNAC_USER, DNAC_PASSWORD

# Disable SSL warnings for sandbox
urllib3.disable_warnings()

# MongoDB setup (assume running on localhost for now)
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['dnac_logs']
logs = db['interactions']

class DNAC_Manager:
    def __init__(self, token=None):
        self.token = token
    
    def get_auth_token(self, display_token=False):
        try:
            url = f"https://{DNAC_IP}:{DNAC_PORT}/dna/system/api/v1/auth/token"
            response = requests.post(
                url,
                auth=HTTPBasicAuth(DNAC_USER, DNAC_PASSWORD),
                verify=False,
                timeout=10
            )
            response.raise_for_status()
            self.token = response.json()['Token']
            return self.token, True, None
        except Exception as e:
            return None, False, str(e)

    def get_network_devices(self):
        if not self.token:
            return None, False, "⚠️ Please authenticate first!"
        try:
            url = f"https://{DNAC_IP}:{DNAC_PORT}/api/v1/network-device"
            headers = {"X-Auth-Token": self.token}
            response = requests.get(
                url, 
                headers=headers, 
                verify=False,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('response', []), True, None
        except Exception as e:
            return None, False, str(e)

    def get_device_interfaces(self, device_ip):
        if not self.token:
            return None, False, "⚠️ Please authenticate first!"
        try:
            devices, ok, err = self.get_network_devices()
            if not ok:
                return None, False, err
            device = next((d for d in devices if d.get('managementIpAddress') == device_ip), None)
            if not device:
                return None, False, f"❌ Device {device_ip} not found!"
            url = f"https://{DNAC_IP}:{DNAC_PORT}/api/v1/interface"
            headers = {"X-Auth-Token": self.token}
            params = {"deviceId": device['id']}
            response = requests.get(
                url,
                headers=headers,
                params=params,
                verify=False,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('response', []), True, None
        except Exception as e:
            return None, False, str(e)

def log_interaction(action, ip=None, result="success", error=None):
    try:
        logs.insert_one({
            "timestamp": datetime.datetime.utcnow(),
            "action": action,
            "device_ip": ip,
            "result": result,
            "error": error
        })
    except Exception as e:
        print(f"[MongoDB Logging Error] {e}")

def menu_view(request):
    context = {
        "output": None,
        "error": None,
        "token": request.session.get('dnac_token'),
        "show_ip_prompt": False,
        "device_ip": ""
    }
    if request.method == "POST":
        choice = request.POST.get("choice", "").strip()
        dnac = DNAC_Manager(request.session.get('dnac_token'))
        if choice == "1":
            token, ok, err = dnac.get_auth_token(display_token=True)
            if ok:
                request.session['dnac_token'] = token
                context["output"] = f"Authentication successful!\nToken: {token}"
                log_interaction("auth", result="success")
            else:
                context["error"] = f"❌ Authentication failed: {err}"
                log_interaction("auth", result="failure", error=err)
        elif choice == "2":
            if not dnac.token:
                context["error"] = "⚠️ Please authenticate first!"
            else:
                devices, ok, err = dnac.get_network_devices()
                if ok:
                    context["output"] = devices
                    log_interaction("devices", result="success")
                else:
                    context["error"] = f"❌ Failed to get devices: {err}"
                    log_interaction("devices", result="failure", error=err)
        elif choice == "3":
            if not dnac.token:
                context["error"] = "⚠️ Please authenticate first!"
            else:
                context["show_ip_prompt"] = True
        elif choice == "4":
            return render(request, "dna_center_cisco/goodbye.html")
        else:
            context["error"] = "❌ Invalid choice. Please try again."
    elif request.method == "GET" and "device_ip" in request.GET:
        # Handle device IP submission for option 3
        device_ip = request.GET.get("device_ip", "").strip()
        dnac = DNAC_Manager(request.session.get('dnac_token'))
        if not dnac.token:
            context["error"] = "⚠️ Please authenticate first!"
        else:
            interfaces, ok, err = dnac.get_device_interfaces(device_ip)
            if ok:
                context["output"] = {"interfaces": interfaces, "device_ip": device_ip}
                log_interaction("interfaces", ip=device_ip, result="success")
            else:
                context["error"] = f"❌ Failed to get interfaces: {err}"
                log_interaction("interfaces", ip=device_ip, result="failure", error=err)
    return render(request, "dna_center_cisco/menu.html", context)
