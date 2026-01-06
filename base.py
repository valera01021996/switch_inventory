from netmiko import ConnectHandler
import requests
import json

class NetmikoBase:
    def __init__(self, device):
        self.device = device
        self.conn = None

    def connect(self):
        self.conn = ConnectHandler(**self.device)

    def disconnect(self):
        if self.conn:
            self.conn.disconnect()

    def cmd(self, command):
        return self.conn.send_command(command, strip_command=True, strip_prompt=True)



class EAPIBase:
    def __init__(self, host, username, password, port=80):
        self.url = f"http://{host}:{port}/command-api"
        self.auth = (username, password)
        self.headers = {"Content-Type": "application/json"}

    
    def cmd(self, commands):
        payload = {
            "jsonrpc": "2.0",
            "method": "runCmds",
            "params": {
                "version": 1,
                "cmds": commands,
                "format": "json",
            },
            "id": 1,
        }

        r = requests.post(self.url, headers=self.headers, auth=self.auth, json=payload, verify=False, timeout=10)
        r.raise_for_status()
        return r.json()["result"]


