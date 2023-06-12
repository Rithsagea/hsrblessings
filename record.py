import keyboard
import pyautogui
import pygetwindow
import yaml
import cv2
import numpy as np
from PIL import Image

# grey hsl(234, 10%, 38%)
# blue hsl(226, 50%, 47%)
# black hsv(225, 19%, 8%)
# true is 2*, false is 1*


def get_rarity(img):
    cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(img)
    img = cv2.bitwise_and(img, img, mask=cv2.inRange(v, 20, 100))
    mean = cv2.mean(s, mask=cv2.inRange(v, 20, 100))[0]
    # print(mean)
    return 1 if mean > 50 else 2


def record_frame():
    print("record frame")
    window: pygetwindow.Win32Window = pygetwindow.getWindowsWithTitle(
        config["emulator"])[0]
    img = np.array(pyautogui.screenshot(region=window.box).convert("RGB"))

    height, width, channels = img.shape
    left = img[height//4:height//2, width * 1 // 8:width * 3 // 8]
    middle = img[height//4:height//2, width * 3 // 8:width * 5 // 8]
    right = img[height//4:height//2, width * 5 // 8:width * 7 // 8]

    print("{} {} {}".format(get_rarity(left),
          get_rarity(middle), get_rarity(right)))


def save_run():
    print("save run")


config = yaml.safe_load(open("config.yml"))
print(config)

keyboard.add_hotkey(config["hotkeys"]["record_frame"], record_frame)
keyboard.add_hotkey(config["hotkeys"]["save_run"], save_run)
keyboard.wait()
