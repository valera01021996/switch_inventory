import re
from base import NetmikoBase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class HuaweiBase(NetmikoBase):
    def get_serial(self):
        commands = [
            "display esn",
            "display device manuinfo",
            "display sn license",
            "display sn",
        ]

        for command in commands:
            try:
                out = self.cmd(command)
                logger.info(f"[{self.device.get('host', 'unknown')})] Command '{command}' output (first 200 chars): {out[:200]}
            except Exception:
                logger.warning(f"[{self.device.get('host', 'unknown')}] Command '{command}' failed {e}")
                continue

            # ESN of slot 0: 102515094903
            m = re.search(r"ESN\s+of\s+slot\s+\d+\s*:\s*([A-Z0-9]+)", out, re.IGNORECASE)
            if m:
                return m.group(1).strip()

            # Slot 1 ESN: XXXXX
            m = re.search(r"\bESN:\s*([A-Z0-9]+)\b", out, re.IGNORECASE)
            if m:
                return m.group(1).strip()

            # Serial Number / SN
            m = re.search(r"\b(Serial Number|SN)\s*[:=]\s*([A-Z0-9\-]+)\b", out, re.IGNORECASE)
            if m:
                return m.group(2).strip()
        logger.warning(f"[{self.device.get('host', 'unknown')}] Serial not found, returning None")
        return None

    def get_interfaces(self):
        out = self.cmd("display interface description")
        interfaces = []

        lines = out.splitlines()
        start = False

        for line in lines:
            line = line.rstrip()

            if line.startswith("Interface"):
                start = True
                continue

            if not start or not line.strip():
                continue

            parts = line.split()
            if len(parts) < 3:
                continue

            iface = parts[0]

            # исключаем логические/агрегации/служебные
            if iface.startswith(("Eth-Trunk", "Vlanif", "LoopBack", "NULL", "MEth")):
                continue

            desc = " ".join(parts[3:]) if len(parts) > 3 else ""

            interfaces.append({"name": iface, "description": desc})

        return interfaces

    def collect(self):
        data = {}
        data["version"] = self.get_version()    # будет разный в наследниках
        data["serial"] = self.get_serial()
        data["interfaces"] = self.get_interfaces()
        data["ports_count"] = len(data["interfaces"])
        return data


class HuaweiVRP(HuaweiBase):
    def get_version(self):
        out = self.cmd("display version")
        m = re.search(r"VRP\s+\(R\)\s+software,\s+Version\s+([^\s,]+)", out)
        return m.group(1) if m else None


class HuaweiYunShan(HuaweiBase):
    def get_version(self):
        out = self.cmd("display version")

        m = re.search(r"^Version\s+([0-9.]+)\s*\(([^)]+)\)", out, re.MULTILINE)
        if m:
            return f"{m.group(1)} ({m.group(2)})"

        m = re.search(r"^Version\s+(.+)$", out, re.MULTILINE)
        return m.group(1).strip() if m else None
