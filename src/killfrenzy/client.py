import asyncio

import json

import kilimanjaro
from .socket import *

import traceback

async def handle_data(data):
    if "code" in data and "type" in data:
        print("[KF] handle_data() :: Returned code => " + str(data["code"]) + ". Type => " + str(data["type"]) + ".")

        return

    if "type" not in data:
        return
    
    if "data" not in data:
        return

    # Handle a full config update.
    if data["type"] == "full_update":
        print("[KF] Received full update. Updating file...")

        # Output JSON pretty print.
        json_data = json.dumps(data["data"], indent=4)

        # Write to Kilimanjaro config file.
        with open("/etc/kilimanjaro/kilimanjaro.json", "w") as file:
            file.write(json_data)

    # Send to KM socket (in JSON format).
    if kilimanjaro.client.is_connected() is True:
        try:
            await kilimanjaro.client.send_data_json(data)
        except Exception as e:
            print("[KF] handle_data() :: Failed to send data to KM.")
            print(e)

async def recv_updates():
    while True:
        try:
            data = await client.recv_data()
        except websockets.exceptions.ConnectionClosedError:
            return
        except websockets.exceptions.ConnectionClosedOK:
            await sleep(1)
            continue

        try:
            json_data = json.loads(data)
        except Exception as e:
            print("[KF] recv_updates() :: Failed to parse JSON.")
            print("[KF] JSON Data => " + data)
            print(e)

        await handle_data(json_data)

async def request_updates():
    while True:
        data = {}
        data["type"] = "full_update"

        try:
            await client.send_data_json(data)
        except websockets.exceptions.ConnectionClosedOK:
            pass

        await sleep(30)

async def sleep(time):
    await asyncio.sleep(time)

async def send_stats():
    while True:
        try:
            file = open("/etc/kilimanjaro/stats", "r")
        except Exception:
            await sleep(1)

            continue

        lines = []

        try:
            lines = file.readlines()
        except Exception as e:
            print("[KF] send_stats() :: Failed to read stats file.")
            print(e)

            await sleep(1)

            continue

        ret = {}
        ret["type"] = "push_stats"
        ret["data"] = {}

        for line in lines:
            info = line.split(':')

            s_type = info[0].strip()
            val = 0

            if len(info) > 1:
                val = info[1].strip()
            
            if s_type == "cpu_load":
                ret["data"][s_type] = int(val)
            else:
                ret["data"][s_type] = val

        #print("Sending stats => " + json.dumps(ret))
        
        try:
            await client.send_data_json(ret)
        except websockets.exceptions.ConnectionClosedOK:
            pass

        await sleep(1)

async def start():
    first_time = True

    # Create tasks.
    p1 = None
    p2 = None
    p3 = None

    # Create an infinite loop that checks if the socket is connected and reconnects if need to be.
    while True:
        # Check if we're connected.
        if client.is_connected() == False:
            if first_time == False:
                print("[KF] Found offline. Reconnecting...")

                # Kill threads.
                try:
                    if p1 is not None and p1.done() is not True:
                        p1.cancel()
                    if p2 is not None and p2.done() is not True:
                        p2.cancel()
                    if p3 is not None and p3.done() is not True:
                        p3.cancel()
                except Exception as e:
                    print("[KF] start() :: Could not cancel tasks.")
                    print(e)

                    await sleep(10)

                    continue
            else:
                first_time = False

            try:
                # Connect to Kill Frenzy's web socket.
                await client.connect()
            except Exception as e:
                print("[KF] start() :: Failed to connect.");
                print(e)
                await sleep(10)

                continue

            # Check if KM is connected.
            if kilimanjaro.client.is_connected():
                to_send = {}
                to_send["type"] = "push_xdp_status"
                to_send["data"] = {}
                to_send["data"]["status"] = True

                try:
                    await client.send_data_json(to_send)
                except Exception as e:
                    print("[KF] start() :: Error updating XDP status.")
                    print(e)

            print("[KF] Connected!")

            try:
                p1 = asyncio.create_task(request_updates())
                p2 = asyncio.create_task(recv_updates())
                p3 = asyncio.create_task(send_stats())
            except Exception as e:
                print("[KF] start() :: At least one task failed at create_task().")
                print(e)
                
                await sleep(10)

                continue

            try:
                tasks = await asyncio.gather(p1, p2, p3)
            except Exception as e:
                print("[KF] start() :: At least one task failed at gather().")
                print(e)
                print(traceback.format_exc())

                await sleep(30)

                continue

        await sleep(30)

def init():
    asyncio.run(start())