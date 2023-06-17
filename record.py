import datetime
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

def get_event(img):
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

    if total < 0.25:
        return 1
    elif total < 0.34:
        return 2
    else:
        return 3


def get_reroll(img):
    height, width, channels = img.shape
    img = img[height*3//4:height, width//2:width*3//4]
    mean = cv2.mean(img)[0]
    return mean < 50


def get_frame(frameCount):
    window: pygetwindow.Win32Window = pygetwindow.getWindowsWithTitle(
        config["emulator"])[0]
    window.activate()
    img = np.array(pyautogui.screenshot(region=window.box).convert("RGB"))

    height, width, channels = img.shape
    left = img[height//4:height//2, width * 1 // 8:width * 3 // 8]
    middle = img[height//4:height//2, width * 3 // 8:width * 5 // 8]
    right = img[height//4:height//2, width * 5 // 8:width * 7 // 8]

    rarities = [get_rarity(left), get_rarity(middle), get_rarity(right)]
    event = get_event(img)
    reroll = get_reroll(img)

    return rarities, reroll, event


class BlessingFrame:
    def __init__(self, rarities, reroll, event, blessing_count):
        self.rarities = rarities
        self.reroll = reroll
        self.blessing_count = blessing_count

        if reroll:
            self.blessing_count -= 1

        self.rarities_count = self.rarities.count(1)

        if 3 in rarities:
            self.event = "EL"  # elite
        elif event == 1:
            if blessing_count == 0 or (blessing_count == 1 and reroll):
                self.event = "BC"  # blessing cosmos
            else:
                self.event = "HS"  # herta's shop
        elif event == 2:
            self.event = "NO"  # normal
        else:
            self.event = "EX"  # extra blessing


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.blessing_data: list[BlessingFrame] = []

        self.title("HSR Blessings Recording Tool")

        self.recordButton = tk.Button(
            self, text="Record Frame", command=self.record_frame)
        self.recordButton.grid(row=0, column=0, padx=10, pady=10)

        self.save_button = tk.Button(
            self, text="Save Run", command=self.save_run)
        self.save_button.grid(row=0, column=1, padx=10, pady=10)

        self.log_text = tk.Text(self)
        self.log_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        keyboard.add_hotkey("ctrl+shift+1", self.record_frame)
        keyboard.add_hotkey("ctrl+shift+2", self.save_run)

    def update_log(self):
        text = ""

        for id, frame in enumerate(self.blessing_data):
            text += "{},{},{},{},{},{},{},{}\n".format(
                id + 1, frame.event, frame.reroll,
                frame.rarities[0], frame.rarities[1], frame.rarities[2],
                frame.rarities_count, frame.blessing_count)

        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, text)

    def get_blessing_count(self):
        blessings = 0
        for frame in self.blessing_data:
            if not frame.reroll and 3 not in frame.rarities:
                blessings += 1
        return blessings

    def record_frame(self):
        frame_count = int(self.log_text.index('end-1c').split('.')[0])
        rarities, reroll, event = get_frame(frame_count)
        self.blessing_data.append(BlessingFrame(rarities, reroll, event,
                                                self.get_blessing_count()))
        self.update_log()

    def save_run(self):
        data = self.log_text.get("1.0", tk.END)
        self.log_text.delete("1.0", tk.END)
        file = open(
            "data/" + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".csv", "w")
        file.write(data)
        file.close()


config = yaml.safe_load(open("config.yml"))
print(config)

window = Window()
window.mainloop()
