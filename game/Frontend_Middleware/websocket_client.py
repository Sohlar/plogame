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

test("call")
test("bet")
test("fold")
test("check")