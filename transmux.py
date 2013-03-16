#!/usr/bin/python
"""
Transmux H.264 mkv recordings to mp4. Will remove the mkv file if successful.

Usage:
    transmux_mkv_to_mp4 <mkv_filename>
"""
import os
import sys

from docopt import docopt

import glib
glib.threads_init()
import gst


class TransMux(object):
    def __init__(self, mkv_filename, ml, exit_app=False):
        self.ml = ml
        self.exit_status = 0
        self.exit_app = exit_app
        mp4_filename = mkv_filename[:-4] + ".mp4"
        self.pipeline = gst.parse_launch(
            "filesrc location=%s ! matroskademux ! h264parse ! filesink location=%s" % (mkv_filename, mp4_filename))
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message_arrived)
        self.pipeline.set_state(gst.STATE_PLAYING)
        self.ml.run()

    def all_complete(self):
        self.ml.quit()
        if self.exit_app:
            sys.exit(0)

    def error_occurred(self, message):
        self.ml.quit()
        print(message)
        if self.exit_app:
            sys.exit(1)
        self.exit_status = 1

    def on_message_arrived(self, bus, message):
        if message.type == gst.MESSAGE_EOS and message.src == self.pipeline:
            self.pipeline.set_state(gst.STATE_NULL)
            self.pipeline.get_state()
            self.all_complete()
        elif message.type == gst.MESSAGE_ERROR:
            self.pipeline.set_state(gst.STATE_NULL)
            self.pipeline.get_state()
            self.error_occurred(message)



if __name__ == '__main__':
    arguments = docopt(__doc__, version="0.1")
    mkv_filename = arguments["<mkv_filename>"]

    ml = glib.MainLoop()
    TransMux(mkv_filename, ml)
