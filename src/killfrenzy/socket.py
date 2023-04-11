import asyncio
import websockets

import json
import ssl

import config

class kf_socket():
    def __init__(self):
        self.socket = None

    async def connect(self):
        ext = "ws"
        ssl_opt = None

        # Check for SSL.
        if config.cfg.get("ssl") == True:
            ext = "wss"
            ssl_opt = ssl.create_default_context()

        self.socket = await websockets.connect(ext + "://" + config.cfg.get("kf_addr") + ":" + str(config.cfg.get("kf_port")), ssl=ssl_opt, compression=None)

    async def send_data(self, data):
        if self.socket is None:
            return

        await self.socket.send(data)

    async def send_data_json(self, data):
        if self.socket is None:
            return

        data_json = json.dumps(data)
        if data["type"] != "push_stats":
            print("Sending data from KF! " + data_json)

        await self.socket.send(data_json)

    async def recv_data(self):
        if self.socket is None:
            return

        ret = await self.socket.recv()

        return ret

    def is_connected(self):
        if self.socket is None:
            return False

        return self.socket.open

client = kf_socket()