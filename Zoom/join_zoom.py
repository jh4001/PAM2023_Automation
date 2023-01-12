import pyautogui
import os
import time
import threading
from threading import Thread

def join_zoom():
    zoom_url = "ZOOM ROOM URL"
    os.system("open -a zoom.us '{0}'".format(zoom_url))
    time.sleep(15) # sleep for a few seconds to let room load

    # unmute the video
    pyautogui.moveTo(133, 872)
    time.sleep(1)
    pyautogui.click()

    # gallery mode
    # pyautogui.moveTo(1407, 62)
    # pyautogui.click()
    # pyautogui.moveTo(1350, 133)
    # pyautogui.click()
    
    # open the statistics page of the Zoom settings
    pyautogui.moveTo(87, 13)
    pyautogui.click()
    pyautogui.moveTo(151, 65)
    pyautogui.click()
    time.sleep(1)
    pyautogui.moveTo(437, 495)
    pyautogui.click()
    pyautogui.moveTo(896, 166)
    pyautogui.click()

def leave_zoom():
    pyautogui.moveTo(1398, 874)
    pyautogui.click()
    pyautogui.moveTo(1320, 770)
    pyautogui.click()
    # pass

def switch_video_overall(duration):
    start = int(time.time())
    overall = False
    while True:
        if overall:
            pyautogui.moveTo(635, 164)
            pyautogui.click()
            overall = False
        else:
            pyautogui.moveTo(896, 166)
            pyautogui.click()
            overall = True
        now = int(time.time())
        if now - start > duration:
            break

def capture_statistics(duration, filename):
    pyautogui.moveTo(937, 560)
    pyautogui.click()
    os.system('ffmpeg -y -f avfoundation -pix_fmt yuyv422 -i "2:" -t {duration} -vf crop=960:400:1180:414 -r 30 {filename} 2> /dev/null &'.format(duration=duration, filename=filename));
    time.sleep(3)
    nlc_thread = Thread(target=switch_video_overall,args=(duration, ))
    nlc_thread.start()

def start_recording():
    pyautogui.moveTo(816, 878)
    time.sleep(1)
    pyautogui.click()

def main():
    duration = 60
    join_zoom()
    capture_statistics(duration)
    time.sleep(duration)
    leave_zoom()

if __name__ == "__main__":
    main()
