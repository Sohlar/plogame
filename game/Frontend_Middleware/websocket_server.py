#!/usr/bin/env python

import asyncio
import json
from websockets.asyncio.server import serve

def get_ai_action(action):
    '''
    For passing data to the ai and waiting for it's return.
    '''
    return

def fetch_db_data():
    '''
    Pull info from the database.
    '''
    return

def validate_action(action):
    '''
    Check if the action sent is valid.
    '''
    action_list = ["call", "check", "fold"]
    valid_action = 0
    for act in action_list:
        if action[0] == act:
            print("Need to validate action is valid assuming "+act+" is valid") # replace this with action valid
            valid_action = 1
    if action[0] == "bet":
        print("Need to validate amount is valid for now assuming bet is valid") # replace this statement with validator
        valid_action = 1
    return valid_action

def check_for_action_value(msg):
    #print("message: "+msg)
    parsed = msg.split(":")
    return validate_action(parsed)

def decode_ws_data(json_cmd):
    # Convert JSON String to Python
    try:
        hand_details = json.loads(json_cmd)
        act = hand_details['action']
        if check_for_action_value(act) == 1:
            return "Valid Action was logged game state incoming" # need to return the state of the game
        else:
            raise Exception("Action "+act+" was not valid")

    except:
        print("Bad action")
        return "Invalid Requested Action" # tell the client they have sent an invalid value

async def super_loop(websocket):
    async for message in websocket:
            ret_msg = decode_ws_data(message)
            await websocket.send(ret_msg)

async def main():
    async with serve(super_loop, "localhost", 8765):
        await asyncio.get_running_loop().create_future()  # run forever

asyncio.run(main())