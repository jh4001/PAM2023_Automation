from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os, sys
import time, datetime, json
from threading import Thread

def timestamp_print(s):
    ct = datetime.datetime.now()
    print("{0}: {1}".format(ct, s))

def milliseconds_to_wait():
    ct = datetime.datetime.now()
    s = int(ct.strftime("%S"))
    ms = int(int(ct.strftime("%f"))/1000)
    return 60 - (s + ms / 1000)

def get_timestamp():
    date_time = datetime.datetime.now()
    return date_time.strftime("%Y%m%d-%H%M%S")

def create_webdriver():
    options = webdriver.ChromeOptions()
    # set the download directory to be the same directory as the python script
    prefs = {}
    prefs["profile.default_content_settings.popups"]=0
    dir_path = os.getcwd()
    prefs["download.default_directory"] = dir_path
    options.add_experimental_option("prefs", prefs)
    # add some other options
    options.add_argument("--window-size=1440,900") # Set window size to 1440x900, as normal
    options.add_argument("--use-fake-ui-for-media-stream") # Accept camera and microphone permissions automatically
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--user-data-dir=~/Library/Application Support/Google/Chrome")
    options.add_argument("--enable-logging")
    options.add_argument("--vmodule=*/webrtc/*=1")
    service = Service("./chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def load_webrtc(audio=False, video=True):
    jitsi_url = "https://your.domain:4000"
    driver = create_webdriver()
    time.sleep(2)
    driver.get(jitsi_url)
    time.sleep(1)
    join_room_js = "document.getElementById('roomName').value = 'shrimp'; document.getElementById('join').click();"
    driver.execute_script(join_room_js)
    return driver

def load_webrtc_stats(driver, duration, nlc_profile, run):
    driver.execute_script("window.open('');")
    # Switch to the new tab and load the webRTC statistics webpage.
    chwd = driver.window_handles
    driver.switch_to.window(chwd[-1])
    driver.get('chrome://webrtc-internals')
    load_legacy_js = """
            dropdown = document.getElementById("statsSelectElement")
            dropdown.selectedIndex = 1
            dropdown.dispatchEvent(new Event("change"));"""
    driver.execute_script(load_legacy_js)
    time.sleep(duration - 1) # duration - 1 since we already waited 1 second above
    # there is only one button on the entire page, it's the one for downloading the log file
    download_data_js = 'document.querySelectorAll("button")[0].click();'
    driver.execute_script(download_data_js)
    time.sleep(5)
    # move the downloaded file to a new name with timestamp
    new_fn = "stats_client_zoom_{0}-{1}.txt".format(nlc_profile, run)
    os.system('mv webrtc_internals_dump.txt {0}'.format(new_fn))
    return new_fn

def close_browser(driver):
    driver.quit()

def nlc_on():
    command = "nlc on"
    os.system(command)

def set_nlc(profile):
    command = "nlc set {0}"
    os.system(command.format(profile))

def start_obs(duration):
    obs_command = "/Applications/OBS.app/Contents/MacOS/OBS --startvirtualcam"
    timeout_command = "gtimeout -s 9 {0} {1} > /dev/null 2>&1 &".format(duration, obs_command)
    os.system(timeout_command)

def start_tshark(filename, duration):
    command = "/Applications/Wireshark.app/Contents/MacOS/tshark -w {0}.pcapng -a duration:{1} > /dev/null 2>&1 &"
    os.system(command.format(filename, duration))

def threaded_nlc(nlc_profile):
    set_nlc(nlc_profile)

def main():
    duration = 300
    stabilize_time = 120
    nlc_profiles = ["256kbps_UL", "512kbps_UL", "1Mbps_UL", "2Mbps_UL"]
    runs = [7, 7, 7, 7]
    tshark_filename = "~/tmp/tshark_client_webrtc_{nlc}-{run}"
    nlc_on()

    for i, nlc_profile in enumerate(nlc_profiles):
        for run in range(runs[i]):
            # wait until next minute starts
            set_nlc("0msX")
            timestamp_print("Waiting for next minute to start...")
            time.sleep(milliseconds_to_wait())
            timestamp_print("Starting Experiment")
            webrtc_webpage = load_webrtc()
            obs_thread = Thread(target=start_obs,args=(duration + stabilize_time, ))
            obs_thread.start()
            nlc_thread = Thread(target=threaded_nlc,args=(nlc_profile,))
            nlc_thread.start()
            time.sleep(stabilize_time)
            tshark_filename_fmt = tshark_filename.format(nlc=nlc_profile, run=run+1)
            timestamp_print("Starting TShark with file {0}".format(tshark_filename_fmt))
            start_tshark(tshark_filename_fmt, duration)
            data_file = load_webrtc_stats(webrtc_webpage, duration, nlc_profile, run+1)
            close_browser(webrtc_webpage)
            timestamp_print("Experiment Complete")

if __name__ == "__main__":
    main()