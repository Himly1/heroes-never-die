from operator import index
from time import sleep
from turtle import position
from matplotlib.pyplot import axis
import torch
import win32api, win32con
import pyautogui
import numpy as np
from pynput import keyboard
import pybboxes as box
import numpy as np
from pynput.mouse import Controller
import pyautogui as autogui
from ctypes import *
from ctypes import wintypes as w
import ctypes
import pydirectinput
import pandas as pd
SendInput = ctypes.windll.user32.SendInput


pyautogui.FAILSAFE = False
def takeScreenshot():
    #Will take screenshot on fullscreen
    #change the value to your window width and heigh
    frame = np.array(pyautogui.screenshot(region=(0,0,1920,1080)))
    return frame

def loadModel():
    device = torch.device('cuda')
    print(device)
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='ow-cheat_1280_yolo5m_aimPoint_and_enemy.pt', force_reload=False)
    model.to(device)
    return model

model = None
def scan_enemy():
    frame = takeScreenshot()
    rs = model(frame)
    xyxy = rs.pandas().xyxy[0]
    aimPoint = next((filter(lambda v: v[6] == 'aimPoint', xyxy.values)), None)
    if aimPoint is not None:
        # drop the rows which name column equal to 'aimPoint'
        xyxy.drop(xyxy[xyxy['name'] == 'aimPoint'].index)
        
        aimPointX, aimPointY = aimPoint[0], aimPoint[1]
        xyxy['aimPointX'] = aimPointX
        xyxy['aimPointY'] = aimPointY
        return xyxy
    else:
        # empty the frame as no emeny found
        return xyxy.head(0)

def computeTheDistanceOfEnemyToTheAimPoint(enemies):
    for diffDef in [['xmin', 'aimPointX', 'xDist'], ['ymin', 'aimPointY', 'yDist']]:
        enemies[diffDef[2]] = enemies.apply(lambda row: np.abs((row[diffDef[0]] - row[diffDef[1]])), axis=1)

def chooseTheOneWhichCloseToAimPoint(enemies):
    id = enemies['xDist'].idxmin()
    return enemies.iloc[id]

def choose_the_enemy(enemies):
    #Fix me
    # currnetly will randomly choose an anemy
    # for ideal solution it should choose the enemy which close enough to your alignment
    enemies = enemies[enemies['confidence'] > 0.5]
    length = enemies.shape[0]
    if length > 0 :
        computeTheDistanceOfEnemyToTheAimPoint(enemies)
        print(f'The enemies are: \n {enemies}')
        theOne = chooseTheOneWhichCloseToAimPoint(enemies)
        print(f'theOne is \n {theOne}')
        names = ['xmin', 'ymin', 'xmax', 'ymax', 'aimPointX', 'aimPointY']
        values = [(lambda name: theOne[name].astype(int))(name) for name in names]
        return values
    else:
        return None

lucky_guy = None
pydirectinput.PAUSE = 0.001
def lock_enemy():
    try:
        x, y = lucky_guy[0], lucky_guy[1]
        aimPointX, aimPointY = lucky_guy[4], lucky_guy[5]
        # xdiff = np.abs(xdiff) if cx < x else -(np.abs(xdiff))
        # ydiff = np.abs(ydiff) if cy < y else -(np.abs(ydiff))
        print(f'x = {x} aimPointX = {aimPointX} theDist is {x - aimPointX}')
        xdist = (x - aimPointX).astype(int)
        xdist = xdist if xdist > -1 else xdist + 50 
        pydirectinput.moveRel(xOffset= xdist, yOffset=0 ,relative=True)
    except BaseException as err:
        print(f'err occred while aiming at the enemy err: ${err}')

def on_press(key):
    if(key == keyboard.Key.shift and lucky_guy != None):
        lock_enemy()

def init():
    global model 
    model = loadModel()
    lis = keyboard.Listener(on_press=on_press)
    lis.start()



init()
while True:
    enemies = scan_enemy()
    lucky_guy = choose_the_enemy(enemies=enemies)

