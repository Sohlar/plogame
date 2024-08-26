#!/usr/bin/env python

import asyncio
from websockets.sync.client import connect

uri = "localhost"
port = "8765"

def test(msg):
    with connect("ws://"+uri+":"+port) as websocket:
        websocket.send(msg)
        message = websocket.recv()
        print(f"Received: {message}")

test("{\"id\": \"1\", \"name\": \"demo\", \"count\": \"0\", \"action\": \"call:0\"}")
test("{\"id\": \"1\", \"name\": \"demo\", \"count\": \"0\", \"action\": \"bet:50\"}")
test("{\"id\": \"1\", \"name\": \"demo\", \"count\": \"0\", \"action\": \"fold:0\"}")
test("{\"id\": \"1\", \"name\": \"demo\", \"count\": \"0\", \"action\": \"check:0\"}")