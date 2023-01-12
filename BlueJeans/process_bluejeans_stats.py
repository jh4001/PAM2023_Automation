import os
import pytesseract
import matplotlib.pyplot as plt
import matplotlib.cm as mcm
import re, json
from datetime import datetime

video_stats = {}
FPS = "fps"
RES = "resolution"
LOSS = "packet_loss"
RTT = "latency" # latency is not processed well by the OCR library
JTR = "jitter"
UL = "upload"
DL = "download"
T = "time"
BW = "bandwidth"
BW_T = "bandwidth_time"

# in case of failure to read image, keep track of most recent stat
most_recent_stat = {} 
# record how many frames had problems for each stat
problem_frames = {}

def log(msg):
    now = datetime.now()
    t_string = now.strftime("%d/%m/%Y %H:%M:%S:%f")
    print("{time}: {msg}".format(time=t_string,msg=msg)) 

def get_image_frames(video):
    os.system('mkdir /tmp/images')
    os.system('ffmpeg -i {video} -vf "select=not(mod(n\,30))" -vsync vfr -f image2 /tmp/images/zoomstats-%d.png 2> /dev/null'.format(video=video))

def clear_image_frames():
    os.system('rm -rf /tmp/images')

def build_stats_datastructure():
    for d in [UL, DL]:
        video_stats[d] = {}
        video_stats[d][FPS] = []
        video_stats[d][RES] = []
        video_stats[d][LOSS] = []
        video_stats[d][RTT] = []
        video_stats[d][JTR] = []
        video_stats[d][BW] = []
        video_stats[d][T] = []
        video_stats[d][BW_T] = []
        most_recent_stat[d] = {}
        most_recent_stat[d][FPS] = 0
        most_recent_stat[d][RES] = 0
        most_recent_stat[d][LOSS] = 0
        most_recent_stat[d][RTT] = 0
        most_recent_stat[d][JTR] = 0
        most_recent_stat[d][BW] = 0
        problem_frames[d] = {}
        problem_frames[d][FPS] = 0
        problem_frames[d][RES] = 0
        problem_frames[d][LOSS] = 0
        problem_frames[d][RTT] = 0
        problem_frames[d][JTR] = 0
        problem_frames[d][BW] = 0

def process_frame(filename, current_time):
    resolution_matcher = re.compile("[0-9]+ x ([0-9]+)")
    stats = pytesseract.image_to_string(filename)
    # print(stats)
    resolutions = resolution_matcher.findall(stats)
    # print(resolutions)
    if len(resolutions) != 2:
        video_stats[UL][RES].append(most_recent_stat[UL][RES])
        video_stats[DL][RES].append(most_recent_stat[DL][RES])
    else:
        video_stats[UL][RES].append(int(resolutions[0]))
        video_stats[DL][RES].append(int(resolutions[1]))
        most_recent_stat[UL][RES] = int(resolutions[0])
        most_recent_stat[DL][RES] = int(resolutions[1])

def get_video_statistics():
    _, _, files = next(os.walk("/tmp/images"))
    file_count = len(files)
    time_step = 300.0/file_count
    log("{0} frames saved. Building video statistics".format(file_count))
    build_stats_datastructure()
    base_filename = '/tmp/images/zoomstats-{idx}.png'
    current_time = 0
    for idx in range(file_count):
        filename = base_filename.format(idx=idx+1)
        process_frame(filename, current_time)
        current_time += time_step

def plot_graph(dir, stat, label):
    fig, axs = plt.subplots(1, 1, figsize=(12, 4))
    ax = plt.subplot(1, 1, 1) 
    if stat == BW:
        ax.plot(video_stats[dir][BW_T], video_stats[dir][stat], label=label)
    else:
        ax.plot(video_stats[dir][T], video_stats[dir][stat], label=label)
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
        ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(22)
    ax.set_ylabel(label)
    # ax.set_ylim([0, 70])
    ax.set_xlabel("Time (s)")
    plt.grid()
    plt.savefig('zoom_statistics_{0}_{1}.png'.format(dir, stat), dpi=200, bbox_inches='tight')

def save_video_statistics(filename):
    with open(filename, 'w+') as fp:
        json.dump(video_stats, fp)

def main():
    log("Generating frame pictures...")
    nlc_profiles = ["256kbps_UL", "512kbps_UL", "1Mbps_UL", "2Mbps_UL"]
    stats_filename = "stats_client_zoom_{nlc}-{run}.json"
    video_filename = "~/tmp/bluejeans_stats_{nlc}-{run}.mkv"
    for nlc_profile in nlc_profiles:
        for run in range(7):
            log("{0} Run {1}".format(nlc_profile, run+1))
            log("-----------")
            get_image_frames(video_filename.format(nlc=nlc_profile, run=run+1))
            get_video_statistics()
            save_video_statistics(stats_filename.format(nlc=nlc_profile, run=run+1))
            log("Sent Video Statistics: FPS Problem Frames: {0}, Resolution Problem Frames: {1}, Packet Loss Problem Frames: {2}".format(problem_frames[UL][FPS], problem_frames[UL][RES], problem_frames[UL][LOSS]))
            log("Recv Video Statistics: FPS Problem Frames: {0}, Resolution Problem Frames: {1}, Packet Loss Problem Frames: {2}".format(problem_frames[DL][FPS], problem_frames[DL][RES], problem_frames[DL][LOSS]))
            log("-----------------------")
            clear_image_frames()

if __name__ == "__main__":
    main()