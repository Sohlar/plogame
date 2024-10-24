#!/usr/bin/env python

import asyncio
import websockets

uri = "localhost"
port = "8765"

async def test(msg):
    try:
        async with websockets.connect("ws://"+uri+":"+port) as websocket:
            await websocket.send(msg)
            message = await websocket.recv()
            print(f"Received: {message}")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    messages = [
        "{\"id\": \"1\", \"name\": \"demo\", \"count\": \"0\", \"action\": \"call:0\"}"   
        "{\"id\": \"1\", \"name\": \"demo\", \"count\": \"0\", \"action\": \"bet:50\"}"
        "{\"id\": \"1\", \"name\": \"demo\", \"count\": \"0\", \"action\": \"fold:0\"}"
        "{\"id\": \"1\", \"name\": \"demo\", \"count\": \"0\", \"action\": \"check:0\"}"
    ]
    await asyncio.gather(*(test(msg) for msg in messages))

asyncio.run(main())