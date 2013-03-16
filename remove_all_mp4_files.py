#!/usr/bin/python
"""
remove_all_mp4_files
"""
import os
import time

BASE_DIR = "/tmp/cctv"

def main():
    directories = os.listdir(BASE_DIR)
    for directory in directories:
        mp4_files = os.listdir(os.path.join(BASE_DIR, directory))
        for mp4_file in mp4_files:
            if mp4_file.endswith(".mp4"):
                full_mp4_file = os.path.join(BASE_DIR, directory, mp4_file)
                file_mtime = os.path.getmtime(full_mp4_file)
                if time.time() - file_mtime > 60 * 5:
                    os.unlink(full_mp4_file)

if __name__ == '__main__':
    main()