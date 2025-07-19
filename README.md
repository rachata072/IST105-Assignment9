# Assignment 9: Cisco DNA Center Network Automation (Django)

## Setup Instructions

1. **Clone the repository**
2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
3. **MongoDB:**
   - Ensure MongoDB is running and accessible (default: `mongodb://localhost:27017/`)
   - You can set a different URI with the `MONGO_URI` environment variable.
4. **Configure DNA Center Credentials:**
   - Edit `IST105-Assignment9/get_device_interfaces/dnac_config.py` if needed.
5. **Run Django migrations:**
   ```
   python manage.py migrate
   ```
6. **Start the Django server:**
   ```
   python manage.py runserver
   ```
7. **Access the app:**
   - Authentication: [http://localhost:8000/auth/](http://localhost:8000/auth/)
   - Devices: [http://localhost:8000/devices/](http://localhost:8000/devices/)
   - Interfaces: [http://localhost:8000/interfaces/?ip=DEVICE_IP](http://localhost:8000/interfaces/?ip=DEVICE_IP)

## Features
- Authenticate to Cisco DNA Center (REST API)
- List network devices
- Show device interfaces
- Log all interactions to MongoDB (`dnac_logs.interactions`)
