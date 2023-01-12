import pyautogui
import os
import time
import threading
from threading import Thread

def join_bluejeans():
    bj_url = "BLUEJEANS ROOM URL"
    os.system("open -a 'Google Chrome' '{0}'".format(bj_url))
    time.sleep(20) # sleep for a few seconds to let room load
    # unmute the video
    pyautogui.moveTo(635, 78)
    time.sleep(1)
    pyautogui.click()

def leave_bluejeans():
    pyautogui.moveTo(140, 30)
    pyautogui.click()
    pyautogui.moveTo(804, 78)
    time.sleep(1)
    pyautogui.click()
    pyautogui.moveTo(683, 185)
    pyautogui.click()
    pyautogui.moveTo(874, 239)
    pyautogui.click()

def capture_statistics(duration, filename):
    pyautogui.moveTo(140, 30)
    pyautogui.click()
    pyautogui.moveTo(1178, 75)
    time.sleep(1)
    pyautogui.click()
    pyautogui.moveTo(1282, 226)
    time.sleep(1)
    pyautogui.click()
    pyautogui.moveTo(1282, 266)
    time.sleep(1)
    pyautogui.click()
    os.system('ffmpeg -y -f avfoundation -pix_fmt yuyv422 -i "2:" -t {duration} -vf crop=590:208:2264:632 -r 30 {filename} 2> /dev/null &'.format(duration=duration, filename=filename));

def main():
    pass

if __name__ == "__main__":
    main()
