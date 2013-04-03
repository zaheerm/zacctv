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
    for containing_dir, directories, files in os.walk(BASE_DIR):
        mkv_files = [for filename in files if filename.endswith(".mkv")]
        for mkv_file in mkv_files
            full_mkv_file = os.path.join(containing_dir, mkv_file)
            file_mtime = os.path.getmtime(full_mkv_file)
            if time.time() - file_mtime > 60 * 5:
                # let's transmux
                mp4_filename = mkv_file[:-4] + ".mp4"
                if mp4_filename not in files:
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