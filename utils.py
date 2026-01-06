from huawei import HuaweiVRP, HuaweiYunShan
from arista import AristaEOS
import os
from dotenv import load_dotenv

load_dotenv()


def create_collector(platform_name, host, credentials):
    platform_lower = platform_name.lower()
    
    if "vrp" in platform_lower:
        device_params = {
            "device_type": "vrp",
            "host": host,
            "username": credentials["username"],
            "password": credentials["password"],
            "port": credentials["port"],
        }
        return HuaweiVRP(device_params)

    elif "yunshan" in platform_lower or "yun-shan" in platform_lower:
        device_params = {
            "device_type": "yunshan",
            "host": host,
            "username": credentials["username"],
            "password": credentials["password"],
            "port": credentials["port"],
        }
        return HuaweiYunShan(device_params)

    elif "eos" in platform_lower or "arista" in platform_lower:
        return AristaEOS(
            host=host,
            username=credentials["username"],
            password=credentials["password"],
            port=credentials.get("port", 80)
        )
    else:
        raise ValueError(f"Unknown platform: {platform_name}")


def get_credentials_by_platform(platform_name):
    platform_lower = platform_name.lower()

    if "vrp" in platform_lower or "yunshan" in platform_lower:
        return {
            "username": os.getenv("HUAWEI_USERNAME"),
            "password": os.getenv("HUAWEI_PASSWORD"),
            "port": int(os.getenv("HUAWEI_PORT", "22")),
        }

    elif "eos" in platform_lower:
        return {
            "username": os.getenv("ARISTA_USERNAME"),
            "password": os.getenv("ARISTA_PASSWORD"),
            "port": int(os.getenv("ARISTA_PORT", "80")),
        }
    else:
        return {
            "username": os.getenv("USERNAME", "admin"),
            "password": os.getenv("PASSWORD", ""),
            "port": int(os.getenv("PORT", "22")),
        }