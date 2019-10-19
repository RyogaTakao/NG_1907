import subprocess
import os
import sys

def sound_play(path):
    os.system("mpg321 " + path + " &")

def sound_stop():
    os.system("killall mpg321")

def main():
    path = os.path.join("/home/pi/Music", "sample_BPM120_1.mp3")
    sound_play(path)

if __name__ == "__main__":
    main()