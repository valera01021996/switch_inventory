from huawei import HuaweiVRP, HuaweiYunShan
from h3c import H3CComware
from arista import AristaEOS
import os
from dotenv import load_dotenv

load_dotenv()


def create_collector(platform_name, host, credentials):
    platform_lower = platform_name.lower()
    
    if "vrp" in platform_lower:
        device_params = {
            "device_type": "huawei_vrp",
            "host": host,
            "username": credentials["username"],
            "password": credentials["password"],
            "port": credentials["port"],
        }
        return HuaweiVRP(device_params)

    elif "yunshan" in platform_lower or "yun-shan" in platform_lower:
        device_params = {
            "device_type": "huawei_vrp",
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

    elif "h3c" in platform_lower or "comware" in platform_lower:
        device_params = {
            "device_type": "hp_comware",  # Netmiko использует hp_comware для H3C
            "host": host,
            "username": credentials["username"],
            "password": credentials["password"],
            "port": credentials["port"],
        }
        return H3CComware(device_params)


    else:
        raise ValueError(f"Unknown platform: {platform_name}")


def creds_from_profile(profile: str):
    if not profile:
        raise ValueError("Profile name cannot be empty")

    p = profile.upper().strip()

    username = os.getenv(f"CRED_{p}_USERNAME")
    password = os.getenv(f"CRED_{p}_PASSWORD")
    port = os.getenv(f"CRED_{p}_PORT", "22")

    if username is None or password is None:
        raise RuntimeError(f"Credential profile {p} is not fully configured")

    try:
        port_int = int(port)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid port value {port} for profile {p}. Must be an integer.")

    return {
        "username": username,
        "password": password,
        "port": port_int,
    }


def get_credentials(device):
    try:
        cf = device.custom_fields if hasattr(device, "custom_fields") else None
    except AttributeError:
        cf = None

    if not isinstance(cf, dict):
        cf = {}

    profile = cf.get("credential_profile")

    if profile:
        try:
            return creds_from_profile(profile)
        except (RuntimeError, ValueError) as e:
            raise RuntimeError(f"Failed to get credentials from profile for device {device.name}: {e}") from e

    
    raise RuntimeError(f"Device {device.name} has no 'credential_profile' in custom_fields.")

