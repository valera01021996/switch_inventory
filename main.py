from json import load
from netbox_client import NetboxClient
from utils import create_collector, get_credentials_by_platform
import os
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")
NETBOX_URL = os.getenv("NETBOX_URL")




nb = NetboxClient(NETBOX_URL, NETBOX_TOKEN)

devices = nb.get_devices(filters={"role": "sw"})

for device in devices:
    ip = nb.get_device_ip(device)
    credentials = get_credentials_by_platform(device.platform.name)
    collector = create_collector(device.platform.name, ip, credentials)

    if hasattr(collector, 'connect'):
        collector.connect()

    try:
        data = collector.collect()
        logger.info(f"Device {device.name} ({device.platform.name}): collected data keys: {list(data.keys())}")

        serial_value = data.get("serial", "unknown")
        logger.info(f"Device {device.name}: serial value = {repr(serial_value)}, type = {type(serial_value)}, bool check = {bool(serial_value)}")

        nb.add_version(device, data.get("version", "unknown"))
        nb.add_serial(device, serial_value)
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

 