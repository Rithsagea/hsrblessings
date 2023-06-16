import keyboard
import pyautogui
import pygetwindow
import yaml
import cv2
import numpy as np
import tkinter as tk

# grey hsv(234, 10%, 38%)
# blue hsv(226, 50%, 47%)
# gold hsv(30, 50%, 69%)
# black hsv(225, 19%, 8%)
# true is 2*, false is 1*


def get_rarity(img):
    cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(img)
    img = cv2.bitwise_and(img, img, mask=cv2.inRange(v, 20, 100))
    mean = cv2.mean(s, mask=cv2.inRange(v, 20, 100))[0]
    print(mean)
    if mean > 90:
        return 3
    elif mean > 50:
        return 1
    else:
        return 2


# 0 - 0.25 "Please select Blessing"
# 0.25 - 0.34 "Normal enemies, Blessing 1 time(s)"
# 0.34 - 0.5 "select blessing 1 extra time"

def get_event(img, num, rarities):

    if 3 in rarities:
        return "E"  # elite

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = img.shape
    img = img[height//8:height*5//32, 0:width]
    total = 0
    for i in range(0, width):
        mean = cv2.mean(img[:, i])[0]
        if (mean > 100):
            total += 1
        img[:, i] = 255 if mean > 100 else 0

    total /= width

    if total < 0.25:  # cosmos or herta
        return "C" if num == 1 else "H"
    elif total < 0.34:  # normal enemy
        return "N"
    else:  # extra blessing
        return "EX"


def get_reroll(img):
    height, width, channels = img.shape
    img = img[height*3//4:height, width//2:width*3//4]
    mean = cv2.mean(img)[0]
    return mean < 50


def record_frame():
    print("record frame")
    window: pygetwindow.Win32Window = pygetwindow.getWindowsWithTitle(
        config["emulator"])[0]
    window.activate()
    img = np.array(pyautogui.screenshot(region=window.box).convert("RGB"))

    height, width, channels = img.shape
    left = img[height//4:height//2, width * 1 // 8:width * 3 // 8]
    middle = img[height//4:height//2, width * 3 // 8:width * 5 // 8]
    right = img[height//4:height//2, width * 5 // 8:width * 7 // 8]

    number = int(logText.index('end-1c').split('.')[0])
    rarities = [get_rarity(left), get_rarity(middle), get_rarity(right)]
    event = get_event(img, number, rarities)
    reroll = get_reroll(img)

    logText.insert(tk.END, "{}, {}, {}: {},{},{}\n".format(
        number, event, reroll,
        rarities[0], rarities[1], rarities[2]))


def save_run():
    print("save run")


config = yaml.safe_load(open("config.yml"))
print(config)

window = tk.Tk()
window.title("HSR Blessings Recording Tool")

recordButton = tk.Button(window, text="Record Frame", command=record_frame)
recordButton.grid(row=0, column=0, padx=10, pady=10)

saveButton = tk.Button(window, text="Save Run", command=save_run)
saveButton.grid(row=0, column=1, padx=10, pady=10)

logText = tk.Text(window)
logText.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(1, weight=1)

keyboard.add_hotkey(config["hotkeys"]["record_frame"], record_frame)
keyboard.add_hotkey(config["hotkeys"]["save_run"], save_run)

window.mainloop()
