#!/usr/bin/python
"""
remove_all_mp4_files
"""
import os
import time

BASE_DIR = "/tmp/cctv"

def older_than(filename, minutes=300):
    if time.time() - os.path.getmtime(filename) > minutes:
        return True
    else:
        return False

def main():
    for containing_dir, directories, files in os.walk(BASE_DIR):
        mp4_files = [mp4_file for mp4_file in files if mp4_file.endswith(".mp4")]
        for mp4_file in mp4_files:
            full_mp4_file = os.path.join(containing_dir, mp4_file)
            file_mtime = os.path.getmtime(full_mp4_file)
            if older_than(full_mp4_file, minutes=60*5):
                os.unlink(full_mp4_file)

if __name__ == '__main__':
    main()