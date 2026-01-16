import re
from base import NetmikoBase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class H3CBase(NetmikoBase):
    def get_serial(self):
        """Получение серийного номера устройства H3C."""
        commands = [
            "display device manuinfo",
            "display device",
        ]
        
        for command in commands:
            try:
                out = self.cmd(command)
                logger.info(f"[{self.device.get('host', 'unknown')}] Command '{command}' output (first 200 chars): {out[:200]}")
            except Exception:
                logger.warning(f"[{self.device.get('host', 'unknown')}] Command '{command}' failed")
                continue
            
            # Ищем первый DEVICE_SERIAL_NUMBER не равный NONE
            # Важно: берём только первый (от основного шасси, не от Fan/Power)
            for line in out.splitlines():
                m = re.match(r"DEVICE_SERIAL_NUMBER\s*:\s*(\S+)", line.strip())
                if m and m.group(1).upper() != "NONE":
                    return m.group(1).strip()
        
        logger.warning(f"[{self.device.get('host', 'unknown')}] Serial not found, returning None")
        return None
    
    def get_interfaces(self):
        """Парсинг интерфейсов из display interface brief."""
        out = self.cmd("display interface brief")
        
        host = self.device.get('host', 'unknown')
        logger.info(f"[{host}] Raw output from 'display interface brief' (first 1000 chars):")
        logger.info(f"[{host}] {out[:1000]}")
        
        interfaces = []
        lines = out.splitlines()
        
        in_table = False
        table_type = None  # 'route' or 'bridge'
        
        for line in lines:
            line = line.rstrip()
            
            # Заголовок route mode: Interface Link Protocol Primary IP Description
            if re.match(r"^Interface\s+Link\s+Protocol\s+Primary", line):
                in_table = True
                table_type = 'route'
                logger.info(f"[{host}] Found route mode header: '{line}'")
                continue
            
            # Заголовок bridge mode: Interface Link Speed Duplex Type PVID Description
            if re.match(r"^Interface\s+Link\s+Speed", line):
                in_table = True
                table_type = 'bridge'
                logger.info(f"[{host}] Found bridge mode header: '{line}'")
                continue
            
            # Информационные строки — пропускаем, но не сбрасываем таблицу
            if line.startswith("Brief information") or line.startswith("Link:") or \
               line.startswith("Protocol:") or line.startswith("Speed:") or \
               line.startswith("Duplex:") or line.startswith("Type:"):
                continue
            
            # Пустая строка — сбрасываем таблицу
            if not line.strip():
                in_table = False
                continue
            
            if not in_table:
                continue
            
            parts = line.split()
            if len(parts) < 2:
                continue
            
            iface = parts[0]
            
            # Исключаем логические/служебные интерфейсы
            if re.match(r"^(InLoop|Loop|NULL|REG|Vlan|MGE)", iface, re.IGNORECASE):
                logger.debug(f"[{host}] ⊗ Excluded: {iface}")
                continue
            
            # Извлечение description
            desc = ""
            if table_type == 'route' and len(parts) >= 5:
                # Interface Link Protocol Primary_IP Description...
                # HGE1/0/1  UP   UP       10.0.254.6 Link_To_Leaf1
                # parts: [0]=Interface [1]=Link [2]=Protocol [3]=IP [4+]=Description
                desc = " ".join(parts[4:])
            elif table_type == 'bridge' and len(parts) >= 7:
                # Interface Link Speed Duplex Type PVID Description...
                # GE1/0/33  DOWN auto  A      A    1    SomeDesc
                # parts: [0]=Interface [1]=Link [2]=Speed [3]=Duplex [4]=Type [5]=PVID [6+]=Description
                desc = " ".join(parts[6:])
            
            logger.debug(f"[{host}] ✓ Parsed: {iface} -> '{desc}'")
            interfaces.append({"name": iface, "description": desc})
        
        logger.info(f"[{host}] 📊 Total parsed: {len(interfaces)} interfaces")
        return interfaces
    
    def collect(self):
        """Сбор всех данных об устройстве."""
        data = {}
        data["version"] = self.get_version()
        data["serial"] = self.get_serial()
        data["interfaces"] = self.get_interfaces()
        data["ports_count"] = len(data["interfaces"])
        return data


class H3CComware(H3CBase):
    """H3C устройства на Comware."""
    
    def get_version(self):
        """Извлечение версии Comware."""
        out = self.cmd("display version")
        
        # H3C Comware Software, Version 7.1.070, Release 6710
        m = re.search(r"Version\s+(\d+\.\d+\.\d+),\s+Release\s+(\S+)", out)
        if m:
            return f"{m.group(1)} Release {m.group(2)}"
        
        # Fallback
        m = re.search(r"Version\s+(\d+\.\d+\.\d+)", out)
        return m.group(1) if m else None