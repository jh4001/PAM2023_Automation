import join_bluejeans
import os, sys
import time, datetime, json
from threading import Thread
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as mcm
from matplotlib.lines import Line2D

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

def nlc_on():
    command = "nlc on"
    os.system(command)

def set_nlc(profile):
    command = "nlc set {0}"
    os.system(command.format(profile))

def start_tshark(filename, duration):
    command = "/Applications/Wireshark.app/Contents/MacOS/tshark -w {0}.pcapng -a duration:{1} > /dev/null 2>&1 &"
    os.system(command.format(filename, duration))

def start_obs(duration):
    obs_command = "/Applications/OBS.app/Contents/MacOS/OBS --startvirtualcam"
    timeout_command = "gtimeout -s 9 {0} {1} > /dev/null 2>&1 &".format(duration, obs_command)
    os.system(timeout_command)

def threaded_nlc(nlc_profile):
    set_nlc(nlc_profile)
    # pass

def main():
    duration = 300
    stabilize_time = 120
    nlc_profiles = ["256kbps_UL", "512kbps_UL", "1Mbps_UL", "2Mbps_UL"]
    runs = [7, 7, 7, 7]
    tshark_filename = "~/tmp/tshark_bluejeans_cca_{nlc}-{run}"
    video_filename = "~/tmp/bluejeans_stats_{nlc}-{run}.mkv"
    nlc_on()

    for i, nlc_profile in enumerate(nlc_profiles[1:]):
        for run in range(runs[i]):
            # wait until next minute starts
            set_nlc("0msX")
            timestamp_print("Waiting for next minute to start...")
            time.sleep(milliseconds_to_wait())
            timestamp_print("Starting Experiment")
            join_bluejeans.join_bluejeans()
            obs_thread = Thread(target=start_obs,args=(duration + stabilize_time, ))
            obs_thread.start()
            nlc_thread = Thread(target=threaded_nlc,args=(nlc_profile, default_profile, tstart, tfinish))
            nlc_thread.start()
            time.sleep(stabilize_time)
            tshark_filename_fmt = tshark_filename.format(nlc=nlc_profile, run=run+1)
            timestamp_print("Starting TShark with file {0}".format(tshark_filename_fmt))
            start_tshark(tshark_filename_fmt, duration)
            video_filename_fmt = video_filename.format(nlc=nlc_profile, run=run+1)
            join_bluejeans.capture_statistics(duration, video_filename_fmt)
            time.sleep(duration)
            time.sleep(5) # just sleep a little bit longer to ensure we don't quit before tshark does
            join_bluejeans.leave_bluejeans()
            timestamp_print("Experiment Complete")


if __name__ == "__main__":
    main()