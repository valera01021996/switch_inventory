from base import EAPIBase
from pprint import pprint

class AristaEOS(EAPIBase):

    def get_version_and_serial(self):
        out = self.cmd(["show version"])[0]
        return {
            "version": out["version"],
            "serial": out["serialNumber"],
        }

    def get_interfaces(self):
        out = self.cmd(["show interfaces description"])[0]

        iface_map = out.get("interfaceDescriptions", {})
        interfaces = []

        for name, data in iface_map.items():

            if name.startswith(("Management", "Vlan", "Loopback", "Port-Channel")):
                continue

            interfaces.append(
                {
                    "name": name,
                    "description": data.get("description", "") or "",
                }
            )

        return interfaces
    
    def collect(self):
        info = self.get_version_and_serial()
        interfaces = self.get_interfaces()
        info["interfaces"] = interfaces
        info["ports_count"] = len(interfaces)

        return info

        