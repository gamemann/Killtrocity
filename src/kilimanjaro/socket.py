import asyncio

import json
import ssl

import config

import asyncio

class km_socket():
    def __init__(self):
        self.socket = None
        self.connected = False
        self.reader = None
        self.writer = None
        
    async def connect(self):
        self.reader, self.writer = await asyncio.open_unix_connection(path=config.cfg.get("km_socket_path"))

        self.connected = True

    async def send_data(self, data):
        if self.writer is None or self.writer.is_closing():
            return

        tosend = bytearray(data, encoding='utf8')
        tosend += b'\n'
        
        self.writer.write(tosend)
        await self.writer.drain()

    async def send_data_json(self, data):
        if self.writer is None or self.writer.is_closing() == True:
            return

        data_json = json.dumps(data)

        tosend = bytearray(data_json, encoding='utf8')
        tosend += b'\n'

        self.writer.write(tosend)
        
        try:
            await self.writer.drain()
        except Exception as e:
            pass

    async def recv_data(self):
        data = await self.reader.readuntil(separator=b'\n')

        return data.decode().rstrip('\n')

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()

    def is_connected(self):
        if self.writer is None or self.writer.is_closing() == True:
            return False

        return True 

    async def stress_test(self, array_size=2048, cnt=50):
        to_send = {}
        to_send["type"] = "ping"
        to_send["data"] = {}
        to_send["data"]["random_data"] = []

        for i in range(array_size):
            to_send["data"]["random_data"].append(i)

        for i in range(cnt):
            await self.send_data_json(to_send) 


client = km_socket()