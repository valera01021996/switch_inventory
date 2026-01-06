from netbox_client import NetboxClient
from utils import create_collector
import os
from dotenv import load_dotenv

load_dotenv()

NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")
NETBOX_URL = os.getenv("NETBOX_URL")

credentials = {
    "username": "root",
    "password": "12345678",
    "port": 22,
}


nb = NetboxClient(NETBOX_URL, NETBOX_TOKEN)

devices = nb.get_devices(filters={"role": "sw"})

for device in devices:
    ip = nb.get_device_ip(device)
    
    collector = create_collector(device.platform.name, ip, credentials)

    if hasattr(collector, 'connect'):
        collector.connect()

    try:
        data = collector.collect()
        nb.add_version(device, data.get("version", "unknown"))
        nb.add_serial(device, data.get("serial", "unknown"))
        nb.add_interfaces_and_descriptions(device, data.get("interfaces"), data.get("ports_count", 0))
    finally:
        if hasattr(collector, 'disconnect'):
            collector.disconnect()
        
    

    



# device = {
#     "device_type": "huawei_vrp",
#     "host": "10.10.0.5",
#     "username": "root",
#     "password": "123456",
#     "port": 22,
# }

# sw = HuaweiVRP(device)
# sw.connect()
# data = sw.collect()
# sw.disconnect()

# pprint(data)


# sw = AristaEOS(
#     host="192.168.1.235",
#     username="admin",
#     password="123456",
#     port=80,
# )

# info = sw.collect()

# print(info)

 