#!/usr/bin/env python
import time
import serial #install from pyserial

import os
import openai

import sys #why do we need this ?
import select #why do we need this ?

openai.api_key = "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"


# setup serial connection
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate = 19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
 #   timeout=1
)

# Define VT100 escape sequences
ESC = '\x1b'
CLEAR_SCREEN = ESC + '[2J'
REVERSE = ESC + '[7m'
BLINK = ESC + '[5m'
OFF = ESC + '[0m'

# Functions 
def menu_screen(_menu_items, _selected):
    _screen = CLEAR_SCREEN + OFF
    _screen = _screen + "Please choose from the following options\r\n"
    
    mods = [OFF] * len(_menu_items)
    
    if _selected >= 0:   
        mods[_selected] = REVERSE
    
    for i in range (len(_menu_items)):
        _screen = _screen + str(mods[i]) + "(" + str(i+1) + ") " + _menu_items[i] +"\r\n"
    
    ser.write(_screen.encode())


def get_input(_menu_items, _selected):
    
    Finished = False
    menu_selected = -1
    
    while not Finished:
        
        raw = ser.readline()
        responce = raw.decode("utf-8")
        
        if responce != "":
            print(responce)
            
            try:
                responce = int(responce) -1
                
                if responce > len(_menu_items):
                    menu_selected = _selected
                else:
                    menu_selected = responce
                    
            except:
                menu_selected = _selected
            
            Finished = True
    return menu_selected
                    
                    
        
# Main loop
screen = CLEAR_SCREEN
ser.write(screen.encode())
current_selection = -1

main_menu = ["Lights","GPT","Other"]
lights_menu = ["Red","Greem", "Boo","Back"]

main_loop = True
lights_loop = False
gpt_loop = False


while main_loop:   
    menu_screen(main_menu,current_selection)
    new_selection = get_input(main_menu, current_selection)
    new_selection_str = main_menu[new_selection]
    
    if new_selection_str == "Lights":
        lights_loop = True
        current_selection = -1
        while lights_loop:
            menu_screen(lights_menu, current_selection)
            new_selection = get_input(lights_menu, current_selection)
            new_selection_str = lights_menu[new_selection]
            if new_selection_str == "Back":
                lights_loop = False
                new_selection = -1
            current_selection = new_selection

    elif new_selection_str == "GPT":
        menu_screen(main_menu,new_selection)
        gpt_loop = True
        answer=""
        prompt="Ask Chat GPT 3.5 Turbo a question (type 'quit' to end):\r\n"
        ser.write(prompt.encode("utf-8"))
        while gpt_loop:
            raw = ser.readline()
            question = raw.decode("utf-8")
            if question[0:4] == "quit":
                print("trying to break")
                gpt_loop = False
                new_selection = -1
                break

            if question != "":
                print(question)
                completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=[{"role": "user", "content": question}])
                answer = (completion.choices[0].message.content)
                answer = answer + "\r\n\r\n"
                question = question + "\r\n"
                ser.write(question.encode("utf-8"))
                ser.write(answer.encode("utf-8"))
                
        # end of gpt loop

    #below need to be last line in main menu while loop        
    current_selection = new_selection





