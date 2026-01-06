import pynetbox
from datetime import datetime



class NetboxClient:
    def __init__(self, url: str, token: str):
        self.url = url.rstrip('/')
        self.token = token
        self.nb = pynetbox.api(self.url, token=self.token)

    def get_devices(self, filters: dict = None):
        return self.nb.dcim.devices.filter(**filters) if filters else self.nb.dcim.devices.all()

    def get_device_ip(self, device):
        if device.primary_ip:
            ip_str = str(device.primary_ip.address)
            return ip_str.split("/")[0]
        return None        

    def add_version(self, device, version: str):
        if not version:
            raise ValueError("Version must be a non-empty string")

        try:
            device.comments = f"OS Version : {version}"
            device.save()
        except Exception as e:
            raise RuntimeError(f"Failed to add version to device {device.name}: {e}") from e

    def add_serial(self, device, serial: str) -> None:
        if not serial:
            raise ValueError("Serial must be a non-empty string")
        try:
            device.serial = serial
            device.save()
        except Exception as e:
            raise RuntimeError(f"Failed to update serial to device {device.name}: {e}") from e

    def add_interfaces_and_descriptions(self, device, interfaces: list[dict], ports_count: int) -> None:
        for iface_data in interfaces:
            iface_name = iface_data.get("name")
            iface_description = iface_data.get("description", "")

            try:
                existing_interface = self.nb.dcim.interfaces.get(device_id=device.id, name=iface_name)
                if existing_interface.description != iface_description:
                    existing_interface.description = iface_description
                    existing_interface.save()
            except Exception:
                try:
                    interface_type = self._get_interface_type(iface_name)
                    new_interface = self.nb.dcim.interfaces.create(
                        device=device.id,
                        name=iface_name,
                        type=interface_type,
                        description=iface_description
                    )
                    new_interface.save()
                except Exception as e:
                    print(f"Failed to create interface {iface_name} on device {device.name}: {e}")
        
        # Обновляем описание устройства после обработки всех интерфейсов
        try:
            device.description = f"Ports count: {ports_count}"
            device.save()
        except Exception as e:
            print(f"Failed to update description for device {device.name}: {e}")

    
    def _get_interface_type(self, interface_name:str):
        name_lower = interface_name.lower()
        if "gigabitethernet" in name_lower or name_lower.startswith("ge"):
            return "1000base-t"
        elif "fastethernet" in name_lower or name_lower.startswith("fe"):
            return "100base-tx"
        elif "ten-gigabitethernet" in name_lower or "10ge" in name_lower or "xge" in name_lower:
            return "10gbase-t"
        else:
            return "other"