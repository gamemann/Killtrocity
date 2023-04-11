import asyncio
import killfrenzy

import json
import threading

import config
from .socket import *

async def handle_data(data):
    if data is None:
        return

    info = None

    try:
        info = json.loads(data)
    except Exception as e:
        print("[KM] handle_data() :: Error parsing JSON data.")
        print(data)
        print(e)

        return
        
    if "type" not in info:
        print("[KM] handle_data() :: Data has no type.")

        return
    
    if "data" not in info:
        print("[KM] handle_data() :: Data has no data field.")
        
        return

    # Send to KF socket (in JSON format).
    if killfrenzy.client.is_connected():
        try:
            print("Sending " + json.dumps(info))
            await killfrenzy.client.send_data_json(info)
        except Exception as e:
            print("[KM] handle_data() :: Failed sending data to KF.")
            print(e)

            return

async def recv_updates():
    while not client.reader.at_eof():
        if client.is_connected() is not True:
            break

        try:
            data = await client.recv_data()
        except Exception as e:
            print("[KM] recv_updates() :: Failed to receive data.")
            print(e)

            if client.is_connected():
                try:
                    await client.close()
                except Exception as e:
                    print("[KM] recv_updates() :: Found recv_update() exception, but received exception when closing client.")
                    print(e)

            break

        if data is not None:
            await handle_data(data)

async def sleep(time):
    await asyncio.sleep(time)

async def start():
    first_time = True

    # Create tasks.
    tasks = None
    p1 = None

    while True:
        # If socket isn't connected, try to connect.
        if client.is_connected() == False:
            # See if this is our first time connecting.
            if first_time == False:
                print("[KM] start() :: Connection offline. Reconnecting...")
                
                try:
                    if p1 is not None:
                        p1.cancel()
                except Exception as e:
                    pass

                to_send = {}
                to_send["type"] = "push_xdp_status"
                to_send["data"] = {}
                to_send["data"]["status"] = False

                try:
                    await killfrenzy.client.send_data_json(to_send)
                except Exception as e:
                    print("[KM] start() :: Error updating XDP status on offline.")
                    print(e)
                
            else:
                first_time = False

            try:
                await client.connect()
            except Exception as e:
                print("[KM] start() :: Failed to connect to Kilimanjaro.");
                print(e)

                await sleep(30)

                continue

            # Update status if available.
            to_send = {}
            to_send["type"] = "push_xdp_status"
            to_send["data"] = {}
            to_send["data"]["status"] = True

            try:
                await killfrenzy.client.send_data_json(to_send)
            except Exception as e:
                print("[KM] start() :: Error updating XDP status.")
                print(e)

            print("[KM] Connected!")

            # Send ping request.
            print("[KM] Sending ping request.")
            
            try:
                await client.send_data("{\"type\": \"ping\", \"data\": {}}")
            except Exception as e:
                print("[KM] start() :: Failed to send ping request.")
                print(e)

                await sleep(10)

                continue

            if (config.cfg.get("stress")):
                await client.stress_test(config.cfg.get("stress_array_size"), config.cfg.get("stress_count"))

            # Start receive task.
            p1 = asyncio.create_task(recv_updates())
            tasks = await asyncio.gather(p1)

        # Sleep for 30 seconds.
        await sleep(30)

def init():
    asyncio.run(start())