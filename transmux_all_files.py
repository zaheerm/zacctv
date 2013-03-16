#!/usr/bin/python
"""
transmux_all_files
"""
import os
import time
import glib
glib.threads_init()

from transmux import TransMux

BASE_DIR = "/tmp/cctv"

def main():
    directories = os.listdir(BASE_DIR)
    for directory in directories:
        mkv_files = os.listdir(os.path.join(BASE_DIR, directory))
        for mkv_file in mkv_files:
            if mkv_file.endswith(".mkv"):
                full_mkv_file = os.path.join(BASE_DIR, directory, mkv_file)
                file_mtime = os.path.getmtime(full_mkv_file)
                if time.time() - file_mtime > 60 * 5:
                    # let's transmux
                    mp4_filename = mkv_file[:-4] + ".mp4"
                    if mp4_filename not in mkv_files:
                        print("transmuxing file %s" % (full_mkv_file,))
                        ml = glib.MainLoop()
                        t = TransMux(full_mkv_file, ml)
                        if t.exit_status == 0:
                            print("success, removing %s" % (full_mkv_file,))
                            os.unlink(full_mkv_file)
                        else:
                            print("failure")

if __name__ == '__main__':
    main()