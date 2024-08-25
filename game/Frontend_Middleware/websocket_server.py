#!/usr/bin/env python

import asyncio
from websockets.asyncio.server import serve

def valid_input(input_str):
    valid_codes = [0,1]
    valid_instructions = ["call","bet","check"]
    for instr in valid_instructions:
        if (input_str == instr):
            return 1
    return 0

def strip_message(input_str):
    usercode = 0 # temporary value, eventually sessions will correlate to a user in a running session
    if (valid_input(input_str)==1):
        return "This is updated"
    return "Invalid command"

    
async def echo(websocket):
    async for message in websocket:
            ret_msg = strip_message(message)
            await websocket.send(ret_msg)

async def main():
    async with serve(echo, "localhost", 8765):
        await asyncio.get_running_loop().create_future()  # run forever

asyncio.run(main())